---
name: visual-api
description: Generate a single-file, static HTML document of an API contract in a Swagger-style layout — endpoints grouped by tag, each a collapsible row with method, path, parameters, request body, and responses, plus a schemas section. The endpoints and shapes come from the real source (an OpenAPI spec, route definitions, or a typed router), never from memory. Use when the user asks to visualize, document, or diagram a REST or HTTP API contract as an HTML page.
---

# Visual API — Static API-Contract Documents

Produce one self-contained `.html` file that shows an API contract the way Swagger UI does: endpoints grouped by tag, one collapsible row per endpoint, and each row expands to its parameters, request body, and responses. A schemas section lists the request and response shapes. No CDN, no build step. The file opens offline, from disk.

The output is a **static document**. It renders with no JavaScript. This is the key difference from `visual-schema`: an API contract is text, not an interactive canvas, so it needs no draggable layout and no script to draw it. A reader sees the whole contract in any viewer, including a scriptless preview pane and GitHub Pages.

## When to use

- "Document this API as an HTML page."
- "Show the REST contract for this service."
- "Turn this OpenAPI spec into a readable page."

Do **not** use for: a database schema (use `visual-schema`), an architecture or workflow explainer (use `visual-explainer`), or a plan for an API change (use `visual-plan`). For a plan, `visual-plan` embeds a scoped change view of this format.

## Method (do these in order)

### 1. Extract from the real source — never invent

Read the actual API source: an OpenAPI or Swagger file, the route definitions, a FastAPI/Flask/Express router, or a typed client. For every endpoint record:

- The HTTP method and the path.
- A one-line summary of what it does.
- Whether it needs authentication.
- Every parameter: name, location (`path`, `query`, or `header`), type, and required state.
- The request body: the media type and the schema (a named model, or inline fields).
- Every response: the status code, a short description, and the schema.

Record every shared model: its name and each property with a type and a required state. Do not invent an endpoint, a parameter, a field, or a status code. If the source is ambiguous, ask.

### 2. Group endpoints by tag

Cluster endpoints into named tags (the OpenAPI tags, or the resource groups: `Auth`, `Catalog`, `Orders`, …). A tag gets a short name and a one-line description. Every endpoint belongs to one tag.

### 3. Build the page as static HTML

The document is plain HTML. Use a native `<details>`/`<summary>` element for every collapsible part, so the page needs no JavaScript to expand or collapse. Build each row and table as literal HTML. Never use `innerHTML` from script.

- A **tag section** is a `<details open>`: a `<summary>` with the tag name and description, then the endpoint rows.
- An **endpoint row** is a `<details>` inside the tag: a `<summary>` with the method badge, the path, the summary, an auth mark, and a chevron. The body holds the Parameters, Request body, and Responses.
- A **schema** is a `<details>` in the Schemas section: a `<summary>` with the model name, then a property table.

Optional JavaScript may add only an `Expand all` / `Collapse all` control that toggles the `open` attribute. The content must render with that script removed.

Copy [`examples/bookstore-api.html`](examples/bookstore-api.html) as a skeleton and replace its endpoints and schemas.

## Layout rules

- **Method color.** Give each HTTP method its Swagger color: `GET` blue, `POST` green, `PUT`/`PATCH` orange or teal, `DELETE` red. Show the method as a solid badge. Tint the row border with the same color.
- **Status color.** Color a status code by class: `2xx`/`3xx` green, `4xx` amber, `5xx` red.
- **Parameters table.** Columns: Name (a `*` marks required), In (`path`/`query`/`header`), Type, Description.
- **Request body.** Show the media type and the schema. Reference a named model, or list inline fields.
- **Responses table.** Columns: Code, Description, Schema. Show a dash when there is no body.
- **Schemas.** One collapsible model per row. The property table columns: Property, Type, Required.
- **Legend of colors is optional**, because the method badges and status colors are self-explanatory.

Keep the page one column that scrolls. Do not add a canvas, pan, zoom, or drag.

## Language rules

Every human-readable string — the title, tag names, tag descriptions, summaries, and response descriptions — MUST follow the [`asd-ste100`](../asd-ste100/SKILL.md) skill, strictly. Follow its heading rule: a heading names the real subject and is not a slogan. The title names the API plainly, for example "Bookstore API", not a marketing phrase.

Method names, paths, parameter names, field names, and type names are identifiers. Render them exactly as the source spells them.

## Footguns

- **A JavaScript-built page shows empty in a scriptless viewer.** Do not build the contract from script. Author the endpoints and schemas as static HTML with `<details>`, so a snapshot renderer and a static host both show the whole page.
- **A body reference with no schema.** When a response or request names a model, that model must appear in the Schemas section.

## Verify before finishing

- The page renders with JavaScript disabled: every endpoint, table, and schema still shows.
- Every endpoint from the source appears once; no invented endpoint, parameter, field, or status code; spot-check five fields against the source.
- Every named request or response schema appears in the Schemas section.
- Each method has its color; each status code has its class color.
- The file has zero external requests and no `innerHTML`.
- Every title and heading names its subject plainly, with no marketing phrasing.
