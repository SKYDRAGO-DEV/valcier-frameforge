# VALCIER FRAMEFORGE — GitHub Import Gateway

This repository is currently in the **source-import stage**, not a deployed AI video generation service.

## One-time source upload

1. Download the **VALCIER_FRAMEFORGE_GitHub_Ready.zip** archive provided in the ChatGPT conversation.
2. On this repository page choose **Add file → Upload files**.
3. Upload the archive **as the exact filename** `VALCIER_FRAMEFORGE_GitHub_Ready.zip` at the repository root.
4. Commit it to `main`. Do not manually extract it in GitHub's website.
5. Open **Actions → Import verified FRAMEFORGE source package** and verify the green check.

The workflow accepts **only** the archive with SHA-256:
`b5b933233cadeef78470e3e730bc369027ccd564abb446e43f6829efcfde1534`

On upload, the workflow validates the checksum, safely unpacks the archive, runs Python tests and an API smoke check, commits the extracted source and removes the uploaded ZIP. If Actions are disabled or write permissions are restricted, enable GitHub Actions and allow the job to write repository contents, then rerun. No test result is claimed before the source is imported.

## Run the source after successful import

GitHub Actions is CI, **not** 24/7 web hosting. For interactive development use **Code → Codespaces → Create codespace on main**. In its terminal run:

```bash
bash scripts/run-codespaces.sh
```

Open forwarded port 8000 and keep port visibility **private**. The app is a local/demo-only research prototype and does not generate real images or video. Never expose demo mode on a public port. Stop the Codespace when not in use.

For local running and full research notes, see the actual application README after source import.

**Security notice:** This repository is currently **public**. Do not commit API tokens, `.env`, production data, or proprietary source. To change visibility visit **Settings → General → Danger Zone → Change repository visibility**.

Built as an original independent creative-studio MVP, not a copy of Higgsfield internals.
