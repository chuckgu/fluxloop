# Viewing Results

Learn how to view and analyze test results on the FluxLoop Web Platform.

## Accessing Results

### Via Web Dashboard

1. Log in to [results.fluxloop.ai](https://results.fluxloop.ai)
2. Select a project
3. Select a scenario
4. View the list of recent test runs

### Direct Links

When you run tests locally, the result URL is automatically displayed:

```bash
$ fluxloop test

✅ Test completed successfully

📊 View results at:
https://results.fluxloop.ai/project/customer-support/run/abc123
```

Claude Code also provides the link:

```
/fluxloop test

✅ Test completed

View results: https://results.fluxloop.ai/...
```

## Result Overview

### Test Run Summary

Summary information for each test run:

```
┌─────────────────────────────────────────┐
│ Test Run: password-reset-test           │
│ Status: ✅ Passed                        │
│ Duration: 12.3s                         │
│ Started: 2024-01-15 14:30:00           │
│ Scenarios: 5/5 passed                   │
└─────────────────────────────────────────┘
```

**Key Metrics:**
- **Status**: Passed / Failed / Partial
- **Duration**: Total execution time
- **Scenarios**: Number of scenarios run
- **Success Rate**: Percentage of passed scenarios
- **Token Usage**: Total tokens consumed
- **Cost**: Estimated API cost

### Scenario Results

Detailed results for each scenario:

| Scenario | Status | Duration | Turns | Tokens | Cost |
|----------|--------|----------|-------|--------|------|
| New User | ✅ Pass | 3.2s | 4 | 1,245 | $0.02 |
| Frustrated User | ✅ Pass | 4.1s | 6 | 2,103 | $0.03 |
| Technical User | ❌ Fail | 5.5s | 8 | 3,421 | $0.05 |
| Mobile User | ✅ Pass | 2.8s | 3 | 987 | $0.01 |
| Returning User | ✅ Pass | 3.5s | 5 | 1,654 | $0.02 |

## Conversation View

### Interactive Transcript

View the conversation content for each scenario:

```
┌─────────────────────────────────────────┐
│ Conversation: Frustrated User           │
│ Status: ✅ Passed                        │
│ Duration: 4.1s                          │
│ Turns: 6                                │
└─────────────────────────────────────────┘

👤 User (0.0s)
I can't login! Forgot my password

🤖 Agent (1.2s) [1,245 tokens, $0.02]
I understand how frustrating that can be. I can help
you reset your password right away. Let me send a
reset link to your registered email address.

What email address did you use to register?

👤 User (0.0s)
user@example.com

🤖 Agent (0.9s) [654 tokens, $0.01]
Perfect! I've sent a password reset link to
user@example.com. You should receive it within a
few minutes.

The link will be valid for 24 hours. Once you click it,
you'll be able to create a new password.

Is there anything else I can help you with?

👤 User (0.0s)
No, thanks

🤖 Agent (0.5s) [321 tokens, $0.01]
You're welcome! If you don't receive the email within
10 minutes, please check your spam folder or contact
us again. Have a great day!

✅ Criteria Check: Response contains "reset link" ✓
✅ Criteria Check: Response time < 3s ✓
✅ Criteria Check: Empathetic tone ✓
```

### Trace Details

Detailed information for each message:

**Agent Response Details:**
- **Latency**: Time taken to respond
- **Tokens**: Input/Output token counts
- **Cost**: Estimated cost
- **Model**: Model used (e.g., claude-3-opus-20240229)
- **Context**: Size of context passed

**Metadata:**
- **Tool Calls**: Tools called and their parameters
- **Documents Retrieved**: Documents retrieved in RAG
- **Embeddings**: Embedding vector information
- **Custom Metadata**: User-defined metadata

### Filtering & Search

Filter conversation content:

```
Search in conversation...

Filters:
☑ Show user messages
☑ Show agent messages
☑ Show tool calls
☑ Show errors
□ Show debug info

Sort by:
○ Time (ascending)
● Time (descending)
○ Token count
○ Cost
```

## Performance Analysis

### Time Breakdown

Time spent at each stage:

```
Total Duration: 4.1s

┌─────────────────────────────┐
│ ██████ Model Inference 2.5s │ 61%
│ ███ Context Retrieval 1.2s  │ 29%
│ █ Tool Execution 0.3s       │  7%
│ ▌ Other 0.1s               │  3%
└─────────────────────────────┘
```

### Token Usage

Token usage analysis:

```
Total Tokens: 2,103

Input:  1,234 tokens ($0.018)
Output:   869 tokens ($0.013)
Total:  2,103 tokens ($0.031)

┌─────────────────────────────┐
│ Breakdown by Turn:          │
│ Turn 1:  645 tokens         │
│ Turn 2:  521 tokens         │
│ Turn 3:  456 tokens         │
│ Turn 4:  301 tokens         │
│ Turn 5:  180 tokens         │
└─────────────────────────────┘
```

### Cost Analysis

Cost breakdown:

```
Total Cost: $0.031

By Model:
Claude Opus:    $0.025 (80%)
Claude Sonnet:  $0.004 (13%)
Embeddings:     $0.002 ( 7%)

Daily Spend:    $2.45
Monthly Spend:  $67.20
Projected:      $85.00
```

## Evaluation Results

### Criteria Checks

Evaluation criteria results:

```
┌─────────────────────────────────────────┐
│ Evaluation Criteria                     │
└─────────────────────────────────────────┘

✅ Response contains "reset link"
   Expected: "reset link"
   Found: "I've sent a password reset link"

✅ Response time < 3s
   Expected: < 3000ms
   Actual: 2,850ms

✅ Empathetic tone detected
   Confidence: 0.92
   Phrases: "I understand", "help you", "right away"

❌ Offered alternative contact method
   Expected: phone/chat mention
   Found: none

   Suggestion: Consider offering phone support for
   urgent password reset requests
```

### Pass/Fail Status

Scenario success/failure determination:

- **Passed**: All required criteria met
- **Failed**: One or more required criteria not met
- **Partial**: Only some optional criteria met

## Comparison View

### Multi-Run Comparison

Compare multiple test runs:

```
Select runs to compare:
☑ Run #123 (Jan 15, 2:30 PM) - Current
☑ Run #122 (Jan 15, 1:15 PM) - Baseline
☑ Run #121 (Jan 14, 11:00 AM) - Previous

                  #123    #122    #121    Δ from #122
Success Rate      80%     100%    60%     -20%
Avg Duration      3.5s    3.2s    4.1s    +0.3s
Avg Tokens        1,856   1,654   2,103   +202
Avg Cost          $0.025  $0.022  $0.031  +$0.003
```

### Scenario-Level Comparison

Compare different runs of the same scenario:

```
Scenario: Frustrated User

           Run #123   Run #122   Changes
Status     ✅ Pass    ✅ Pass    -
Duration   4.1s       3.8s       +0.3s
Turns      6          6          -
Tokens     2,103      1,987      +116
Cost       $0.031     $0.029     +$0.002

Differences:
• Turn 2: Added empathy phrase "I understand"
• Turn 3: More detailed explanation (+78 tokens)
• Turn 4: Same response
```

### A/B Testing

Compare two versions of an agent:

```
A/B Test: Password Reset Flow
Version A (Current) vs Version B (Experimental)

                Version A   Version B   Winner
Success Rate    80%         90%         B ⭐
Avg Duration    3.5s        4.2s        A ⭐
User Sentiment  0.75        0.82        B ⭐
Cost per Test   $0.025      $0.031      A ⭐

Overall: Version B wins (3/4 metrics improved)
```

## Exporting Results

### Export Formats

Export results in various formats:

```
Export Results:

Format:
○ JSON (API-compatible)
● CSV (Spreadsheet-ready)
○ PDF (Report)
○ Markdown (Documentation)

Include:
☑ Conversation transcripts
☑ Performance metrics
☑ Evaluation results
□ Debug information
□ Raw API responses

[Export]
```

### CSV Export

CSV for spreadsheets:

```csv
run_id,scenario,status,duration,turns,tokens,cost
123,new-user,passed,3.2,4,1245,0.02
123,frustrated-user,passed,4.1,6,2103,0.03
123,technical-user,failed,5.5,8,3421,0.05
```

### JSON Export

JSON for programmatic analysis:

```json
{
  "run_id": "123",
  "project": "customer-support",
  "timestamp": "2024-01-15T14:30:00Z",
  "scenarios": [
    {
      "name": "frustrated-user",
      "status": "passed",
      "duration_ms": 4100,
      "turns": 6,
      "conversation": [
        {
          "role": "user",
          "content": "I can't login! Forgot my password",
          "timestamp": "2024-01-15T14:30:00.000Z"
        },
        {
          "role": "agent",
          "content": "I understand...",
          "timestamp": "2024-01-15T14:30:01.200Z",
          "tokens": {
            "input": 234,
            "output": 156
          },
          "cost": 0.02
        }
      ],
      "evaluation": {
        "criteria_passed": 3,
        "criteria_total": 4,
        "details": [...]
      }
    }
  ]
}
```

## Sharing Results

### Share Link

Share results with team members:

```
Share this test run:

🔗 Public Link (anyone with link):
https://results.fluxloop.ai/share/abc123def456

🔒 Team-Only Link (requires login):
https://results.fluxloop.ai/project/customer-support/run/123

⏱️ Link expires: Never | 1 day | 1 week | 1 month

[Copy Link]
```

### Email Report

Send report via email:

```
Send Report:

To: team@company.com
Subject: FluxLoop Test Results - Password Reset Flow

Include:
☑ Summary
☑ Failed scenarios
☑ Performance charts
□ Full transcripts

[Send]
```

### Slack Integration

Automatic notifications to Slack:

```
Connected to: #agent-testing

Notify on:
☑ Test completed
☑ Test failed
□ Test passed
□ Performance degraded

Message format:
"✅ Test completed: {scenario} - {status}"

[Update Settings]
```

## Advanced Features

### Custom Dashboards

Create custom dashboards:

- Place specific metric widgets
- Time-based trend charts
- Success rate heatmaps
- Cost tracking graphs

### Alerts & Monitoring

Set up automatic alerts:

```
Alert Rules:

1. Success rate drops below 80%
   → Notify: team@company.com
   → Severity: High

2. Avg response time > 5s
   → Notify: #performance-alerts
   → Severity: Medium

3. Daily cost > $100
   → Notify: finance@company.com
   → Severity: Low
```

### Historical Analysis

Long-term trend analysis:

```
Time Range: Last 30 days

Success Rate Trend:
Jan 1:  85% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Jan 15: 90% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Jan 30: 92% ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Improvement: +7% over 30 days
```

## Next Steps

- [API Keys](./api-keys.md): Create and manage API keys
- [CLI Sync Command](/cli/commands/sync): Upload results with CLI
- [Platform Overview](./platform-overview.md): Web platform overview
