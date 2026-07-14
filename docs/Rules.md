# Technical Rules — Image Craft AI

These guardrails are **locked** as of Phase 1. No phase may silently change them. If a conflict arises, flag it explicitly and get approval before proceeding.

---

## 1. Language & Runtime

| Rule                  | Value                                   |
| --------------------- | --------------------------------------- |
| Python version        | 3.10.x (conda env `imagecraft`)         |
| Dependency pinning    | Exact versions in `requirements.txt`    |
| No bare `>=`          | Every pin justified if not latest stable |

## 2. Architecture

| Rule                                  | Detail                                                                 |
| ------------------------------------- | ---------------------------------------------------------------------- |
| UI framework                          | Gradio — single framework, no Streamlit                                |
| No business logic in UI files         | UI calls services → services call engines                              |
| Engine contract                       | All engines implement `ImageGenerator` ABC                             |
| Engine extensibility                  | Adding a new engine = one new file + one config entry, nothing else    |
| Config-driven switching               | Active engine set via `.env` / config, never hardcoded                  |
| No hardcoded secrets, paths, or magic numbers | Config or `.env` only                                          |

## 3. Code Quality

| Rule                         | Detail                                                          |
| ---------------------------- | --------------------------------------------------------------- |
| Max function length          | 40 lines (if longer, decompose)                                 |
| Single Responsibility (SRP)  | Each class has one reason to change — enforced literally         |
| Type hints                   | Every public function and method, all parameters and return types|
| Docstrings                   | Google style, every public function/class, no exceptions         |
| DRY / KISS / YAGNI           | No speculative abstractions; refactor when duplication appears   |

## 4. Logging & Observability

| Rule                      | Detail                                              |
| ------------------------- | --------------------------------------------------- |
| Logging framework         | `logging` stdlib only                               |
| No bare `print()`         | Every output goes through a logger                  |
| Log levels                | DEBUG for internals, INFO for user-visible flow, WARNING for fallbacks, ERROR for failures |
| Log destination           | Console + rotating file in `logs/`                  |
| Secrets in logs           | Never. API tokens are masked or omitted.            |

## 5. Async & UI Responsiveness

| Rule                              | Detail                                                |
| --------------------------------- | ----------------------------------------------------- |
| No blocking calls in UI thread    | All engine/network calls in background threads/workers |
| Progress feedback                 | Visible within 1 second of starting generation         |
| Timeout                           | All network calls have explicit timeouts               |

## 6. Error Handling

| Rule                              | Detail                                                     |
| --------------------------------- | ---------------------------------------------------------- |
| User-facing messages              | Every error scenario → clear message + suggested action    |
| No raw stack traces in UI         | Full traces go to logs only                                |
| No silent failures                | Every caught exception is logged and surfaced              |
| Graceful degradation              | GPU fails → CPU fallback with warning; cloud fails → clear message |

## 7. Security

| Rule                    | Detail                                             |
| ----------------------- | -------------------------------------------------- |
| `.env` file             | Gitignored, never committed                        |
| `.env.example`          | Committed with placeholder values                  |
| API tokens              | Loaded from env vars or `.env`, never in source     |
| User input              | Prompts are validated/sanitized before passing to engines |

## 8. Testing

| Rule                      | Detail                                                        |
| ------------------------- | ------------------------------------------------------------- |
| Every phase               | At least one smoke test proving the phase deliverable works    |
| Coverage target           | Meaningful coverage on `services/` and `engines/`, not vanity 100% |
| Test types                | Unit, integration, config validation, UI smoke                |
| Test runner               | `pytest`                                                       |

## 9. Documentation

| Rule                           | Detail                                                     |
| ------------------------------ | ---------------------------------------------------------- |
| `Memory.md`                    | Updated at end of every phase, no exceptions               |
| Docs written alongside code    | Not all up front — each doc produced in its designated phase |
| `README.md` / `requirements.txt` | Living drafts, finalized in last phase                  |

## 10. File & Folder Conventions

| Rule                        | Detail                                           |
| --------------------------- | ------------------------------------------------ |
| Generated images            | Saved to `images/`, gitignored                   |
| Logs                        | Saved to `logs/`, gitignored                     |
| Config files                | `src/config/`                                    |
| Models / dataclasses        | `src/models/`                                    |
| Module naming               | `snake_case`, descriptive, no abbreviations      |
