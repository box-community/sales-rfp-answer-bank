# Box RFP answer bank

A minimal, runnable reference app that provisions a
[Box Hub](https://developer.box.com/guides/hubs-api/), indexes curated sales
content, and lets reps ask natural-language questions with
[Box AI](https://developer.box.com/guides/box-ai/ai-tutorials/ask-questions).

A script creates a Sales Hub, adds your Sales Content folder, then another script queries the hub with
`POST /2.0/ai/ask`. An optional HTML page shows how to embed the hub AI chat
in a CRM sidebar.

This is the companion repository to the tutorial: 
**[Build an answer bank with Box Hubs and AI](https://developer.box.com/tutorials/sales-rfp-answer-bank)**.

## What it does

| Capability | How |
| --- | --- |
| Provision a Sales Hub | `POST /2.0/hubs` via `create_hub.py` |
| Index curated folders | `POST /2.0/hubs/:id/manage_items` |
| Manage who can query | Hub collaborations (`manage_access.py`) |
| Answer RFP questions | `POST /2.0/ai/ask` against the hub (`query_hub.py`) |
| Embed in a CRM | Sample `embed.html` (Box Hubs AI Chat embed) |

## Project layout

```
sales-rfp-answer-bank/
├── box_client.py          # CCG auth as a Box user (user_id)
├── create_hub.py          # Create hub + add Sales Content folder
├── manage_access.py       # Add hub collaborators
├── query_hub.py           # Ask Box AI questions against the hub
├── refresh_hub.py         # Add/remove hub folders (reference helpers)
├── embed.html             # CRM embed sample for hub AI chat
├── make_sample_content.py # Generates sample_content/ PDFs
├── sample_content/        # Upload this tree to Box as "Sales Content"
├── requirements.txt
├── .env.example
└── .gitignore
```

## Prerequisites

- **Python 3.11+**
- A [free Box developer account](https://account.box.com/signup/developer),
  or a [Box Enterprise account](https://www.box.com/pricing) with **Box AI**
  and **Box Hubs** enabled. See
  [Configuring Box Hubs](https://support.box.com/hc/en-us/articles/25822332454547-Configuring-Box-Hubs).
- A **Client Credentials Grant (CCG)** Platform App with
  **Generate User Access Tokens** enabled, **authorized** in the Admin Console,
  and these scopes:
  - **Read and write all files and folders stored in Box**
  - **Manage AI**
- Your **Box user ID** (Admin Console → **Users**, or your avatar URL)
- A **Sales Content** folder in Box that the authenticated user can access
  (at least **Viewer**)

## Setup

1. **Clone and enter the project**

   ```bash
   git clone https://github.com/box-community/sales-rfp-answer-bank.git
   cd sales-rfp-answer-bank
   ```

2. **Create a virtual environment and install dependencies**

   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   python -m pip install -r requirements.txt
   ```

3. **Generate and upload sample content** (or use your own approved materials)

   ```bash
   python make_sample_content.py
   ```

   Upload the `sample_content/` folder tree to Box as **Sales Content**
   (or [copy the tutorial's shared sample folder](https://previewteam.app.box.com/s/qq7uws38kuo3fl81fzmjjbgrkemprqlk)).
   Note the top-level folder ID from the URL
   (`https://app.box.com/folder/123456789` > `123456789`).

   > The authenticated user (`BOX_USER_ID`) must have at least **Viewer**
   > access to this folder. If you later switch to a Service Account
   > (`enterprise_id`), invite that account as a collaborator instead.

4. **Configure credentials**

   ```bash
   cp .env.example .env
   ```

   Fill in `BOX_CLIENT_ID`, `BOX_CLIENT_SECRET`, `BOX_USER_ID`, and
   `SALES_CONTENT_FOLDER_ID`. Leave `BOX_HUB_ID` blank — `create_hub.py`
   writes it after provisioning.

   > **Never commit `.env`.** It is already in `.gitignore`.

## Run

**1. Verify authentication**

```bash
python -c "from box_client import get_box_client; c = get_box_client(); u = c.users.get_user_me(); print(f'Authenticated as: {u.name} ({u.login})')"
```

**2. Create the hub and add content**

```bash
python create_hub.py
```

Example output:

```
Created hub: Sales RFP Answer Bank (ID: 12345678)
Added folder 987654321 to hub 12345678

Sales Hub ready. Hub ID: 12345678
```

`BOX_HUB_ID` is written to `.env` automatically.

> Wait a few minutes for Box to index the files before querying. Fresh hubs
> may return empty or incomplete answers until indexing finishes.

**3. Query the hub**

```bash
python query_hub.py
# or ask a specific question:
python query_hub.py What security certifications do we hold?
```

The default questions match facts in `sample_content/` (SLA, EU residency,
certs, volume discounts).

**4. (Optional) Share the hub with sales reps**

```bash
# in .env: SALES_REP_EMAILS=rep1@example.com,rep2@example.com
python manage_access.py
```

**5. (Optional) Embed in a CRM mock**

Open `embed.html`, replace `YOUR_HUB_ID` in the iframe `src`, and open the
page while signed in to Box. See
[Box Hubs AI Chat embedding](https://developer.box.com/guides/embed/box-embed/#box-hubs-ai-chat-embedding).

**6. Verify in Box**

Open [app.box.com](https://app.box.com) > **Hubs**. Your "Sales RFP Answer Bank"
hub should list the Sales Content folder.

## How it works

1. `create_hub.py` creates a hub and adds the Sales Content folder. Nested
   files are indexed; new files added to those folders later are picked up
   automatically.
2. Hubs inherit Box permissions - answers only use content the querying user
   can already access.
3. `query_hub.py` calls Box AI with `items: [{ type: "hubs", id }]` so answers
   stay grounded in approved materials.
4. `refresh_hub.py` has helpers to add or remove folders when the library
   changes.

## Security notes

- Keep client secrets and tokens server-side.
- Prefer `viewer` hub collaborations for reps; reserve `editor` for curators.
- Keep the answer bank curated — outdated proposals and pricing hurt answer
  quality more than missing content.
- Users of an embedded hub chat authenticate with their Box session and need
  at least Viewer on the hub.

## Troubleshooting

| Symptom | Fix |
| --- | --- |
| `unauthorized_client` | Authorize the app (Developer Console → Authorization → Review and Submit). |
| `invalid_client` | Check `BOX_CLIENT_ID` / `BOX_CLIENT_SECRET` / `BOX_USER_ID`. Confirm **Generate User Access Tokens** is enabled. |
| `403` / insufficient permissions | Enable Read/Write file scopes and **Manage AI**; re-authorize after scope changes. |
| `404` adding hub items | Wrong folder ID, or `BOX_USER_ID` lacks Viewer access to the folder. |
| Empty / irrelevant AI answers | Wait for indexing; confirm the hub has files with extractable text (not empty folders or image-only PDFs). |
| Hub missing in Box UI | Add yourself via `manage_access.py`, or confirm Box Hubs is enabled for the account. |

## License

[MIT](./LICENSE)
