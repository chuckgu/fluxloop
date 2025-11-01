---
sidebar_position: 1
---

# LangChain Integration

Use FluxLoop with LangChain.

## Example

```python
import fluxloop
from langchain.chains import LLMChain

@fluxloop.agent()
def run_chain(prompt: str):
    chain = LLMChain(...)
    return chain.run(prompt)
```

## Coming Soon

Full LangChain integration guide is in development.

