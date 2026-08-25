# Public demo console deployment

This bundle deploys only the presentation and Evidence Console. It does not make the three private GCP agents public and does not trigger new GCP assurance runs.

The deployed revision is scale-to-zero (`min=0`) with the currently observed Cloud Run cap of 100 instances, concurrency 20, timeout 120 seconds, 1 CPU, and 512 MiB memory. Uploaded PDF/TXT bytes are processed in an instance temporary directory and are not written to GCS. The public test catalog remains a read-only snapshot.

Deployment target for the 2026-08-25 presentation build:

- project: `iceu-686`
- region: `asia-northeast3`
- service: `spectra-demo-console`
- revision: `spectra-demo-console-00006-6mh` (100% traffic at final verification)
- image digest: `sha256:edeecb043f1bf12acd50b32ee4ac425fae7a5f8ab321e2edefd7b1888c9d6e53`
- public period: through 2026-08-27; remove the service after the event

The public service does not expose a live attack endpoint. Doing so would require Workflow execution or Storage write permissions and would allow unauthenticated callers to create cost, logs, and repeated probe traffic. Attack evidence is therefore replayed from independently verified snapshots.

Removal command after the event:

```bash
gcloud run services delete spectra-demo-console --project=iceu-686 --region=asia-northeast3
```
