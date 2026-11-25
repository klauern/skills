import { expect, test } from "bun:test";
const { assessPrFeedback } = require("../pr_assess_classifier.js");

const options = {
  command: "uv run '/trusted/pr_assess.py' --classifier-input 9",
  provider: "approved",
  modelId: "judge",
};
const model = { provider: options.provider, id: options.modelId, input: ["text"] };
const candidate = {
  display: "[BLOCKING] thread private.py:10 - @reviewer: Not blocking.",
  baseline: "blocking",
  feedback: { opening: "Not blocking.", replies: [{ text: "This can wait.", by_opener: true }] },
};
const baseline = "# PR Assessment\n\n## Comment Triage";
const payload = (items) => ({ report: baseline, items, omitted: 1 });

function harness(items, overrides = {}) {
  const shown = [];
  const calls = [];
  const context = {
    text: (message) => shown.push(message),
    tools: {
      async bash(request) {
        expect(request.command).toBe(options.command);
        return { exit_code: 0, truncated: false, output: JSON.stringify(payload(items)) };
      },
    },
    models: {
      async getAvailableOfType(type, provider) {
        expect({ type, provider }).toEqual({ type: "classifier", provider: options.provider });
        return [model];
      },
      async classify(selected, request) {
        expect(selected).toBe(model);
        expect(shown).toEqual([baseline]);
        calls.push(request);
        return decision();
      },
      ...overrides,
    },
  };
  return { context, shown, calls };
}

function decision(choice = "suggestion", probability = 0.93, confidence = 0.93) {
  return {
    stopReason: "stop",
    responseId: "example-id",
    answers: { intent: { type: "choice", choice, probabilities: { [choice]: probability }, confidence } },
  };
}

test("keeps the keyword report and sends one minimized request per open item", async () => {
  const next = { ...candidate, feedback: { opening: "Can you explain this?", replies: [] } };
  const { context, shown, calls } = harness([candidate, next]);
  const result = await assessPrFeedback(options, context);
  expect(shown).toEqual([baseline]);
  expect(calls.map(({ state }) => state)).toEqual([
    { feedback: candidate.feedback }, { feedback: next.feedback },
  ]);
  expect(calls.map(({ questions }) => Object.keys(questions))).toEqual([["intent"], ["intent"]]);
  expect(result).toMatchObject({ status: "advisory", provider: "approved", model: "judge", omitted: 1 });
  expect(result.items[0]).toEqual({
    status: "classified", baseline: "blocking", display: candidate.display,
    choice: "suggestion", probability: 0.93, confidence: 0.93, responseId: "example-id",
  });
});

test("preserves the baseline on low confidence, invalid labels, or provider failures", async () => {
  const answers = [
    decision("informational", 0.77),
    decision("nit", 0.93, 0.76),
    decision("invented"),
    decision("nit", NaN),
    { stopReason: "error", errorMessage: "private diagnostics" },
    new Error("provider failed"),
    decision(),
  ];
  const { context, shown } = harness(answers.map(() => candidate), {
    async classify() {
      const result = answers.shift();
      if (result instanceof Error) throw result;
      return result;
    },
  });
  const result = await assessPrFeedback(options, context);
  expect(shown).toEqual([baseline]);
  expect(result.items.map((item) => item.baseline)).toEqual(Array(7).fill("blocking"));
  expect(result.items.map((item) => item.status)).toEqual([
    "needs_review", "needs_review", "unavailable", "unavailable", "unavailable", "unavailable", "classified",
  ]);
  expect(JSON.stringify(result)).not.toContain("private diagnostics");
});

test("does not switch providers if the approved model is unavailable", async () => {
  const { context, shown, calls } = harness([candidate], {
    async getAvailableOfType() {
      return [{ ...model, provider: "different" }, { ...model, id: "different" }];
    },
  });
  expect(await assessPrFeedback(options, context)).toEqual({ status: "classifier_unavailable" });
  expect(shown).toEqual([baseline]);
  expect(calls).toEqual([]);
});

test("does not contact the catalog for an empty or invalid sample", async () => {
  let lookups = 0;
  const { context, shown } = harness([], {
    async getAvailableOfType() {
      lookups++;
      return [model];
    },
  });
  expect(await assessPrFeedback(options, context)).toEqual({ status: "no_feedback_sample", omitted: 1 });
  expect(shown).toEqual([baseline]);
  context.tools.bash = async () => ({ exit_code: 0, truncated: true, output: "{}" });
  expect(await assessPrFeedback(options, context)).toEqual({ status: "assessment_unavailable" });
  expect(lookups).toBe(0);
});
