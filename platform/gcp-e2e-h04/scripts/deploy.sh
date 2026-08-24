#!/usr/bin/env bash
set -euo pipefail

H04_PROJECT_ID="${H04_PROJECT_ID:-iceu-686}"
H04_REGION="${H04_REGION:-asia-northeast3}"
H04_BUCKET="${H04_BUCKET:-spectra-h04-${H04_PROJECT_ID}}"
H04_REPOSITORY="spectra-h04"
H04_IMAGE="${H04_REGION}-docker.pkg.dev/${H04_PROJECT_ID}/${H04_REPOSITORY}/agents:h05"
H04_WORKFLOW_SA="spectra-h04-workflow@${H04_PROJECT_ID}.iam.gserviceaccount.com"
H04_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
H04_ROOT="$(cd "${H04_SCRIPT_DIR}/.." && pwd)"
H04_REPO_ROOT="$(cd "${H04_ROOT}/../.." && pwd)"
H04_BUILD_CONTEXT="$(mktemp -d -t spectra-h05-build.XXXXXX)"
trap 'rm -rf "${H04_BUILD_CONTEXT}"' EXIT

if [[ "$(gcloud config get-value project 2>/dev/null)" != "${H04_PROJECT_ID}" ]]; then
  echo "Configured gcloud project is not ${H04_PROJECT_ID}" >&2
  exit 2
fi
if [[ -z "$(gcloud auth list --filter=status:ACTIVE --format='value(account)')" ]]; then
  echo "No active gcloud account" >&2
  exit 2
fi

gcloud services enable \
  run.googleapis.com workflows.googleapis.com workflowexecutions.googleapis.com \
  storage.googleapis.com logging.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com iam.googleapis.com \
  --project="${H04_PROJECT_ID}"

for H04_ROLE in mission parts assurance workflow; do
  H04_SA_NAME="spectra-h04-${H04_ROLE}"
  if ! gcloud iam service-accounts describe "${H04_SA_NAME}@${H04_PROJECT_ID}.iam.gserviceaccount.com" --project="${H04_PROJECT_ID}" >/dev/null 2>&1; then
    gcloud iam service-accounts create "${H04_SA_NAME}" \
      --display-name="SPECTRA H04 ${H04_ROLE}" --project="${H04_PROJECT_ID}"
  fi
done

if ! gcloud storage buckets describe "gs://${H04_BUCKET}" --project="${H04_PROJECT_ID}" >/dev/null 2>&1; then
  gcloud storage buckets create "gs://${H04_BUCKET}" \
    --project="${H04_PROJECT_ID}" --location="${H04_REGION}" \
    --uniform-bucket-level-access --public-access-prevention
fi
gcloud storage buckets update "gs://${H04_BUCKET}" \
  --lifecycle-file="${H04_ROOT}/storage-lifecycle.json" --project="${H04_PROJECT_ID}"

if ! gcloud artifacts repositories describe "${H04_REPOSITORY}" --location="${H04_REGION}" --project="${H04_PROJECT_ID}" >/dev/null 2>&1; then
  gcloud artifacts repositories create "${H04_REPOSITORY}" \
    --repository-format=docker --location="${H04_REGION}" \
    --description="SPECTRA H04 synthetic agent images" --project="${H04_PROJECT_ID}"
fi

python3 "${H04_ROOT}/scripts/stage_build_context.py" \
  --repo-root="${H04_REPO_ROOT}" --output="${H04_BUILD_CONTEXT}"

gcloud builds submit "${H04_BUILD_CONTEXT}" --tag="${H04_IMAGE}" \
  --project="${H04_PROJECT_ID}" --suppress-logs

for H04_ROLE in mission parts assurance; do
  H04_SERVICE="spectra-h04-${H04_ROLE}"
  H04_SA_EMAIL="${H04_SERVICE}@${H04_PROJECT_ID}.iam.gserviceaccount.com"
  gcloud run deploy "${H04_SERVICE}" \
    --image="${H04_IMAGE}" --region="${H04_REGION}" --project="${H04_PROJECT_ID}" \
    --service-account="${H04_SA_EMAIL}" --set-env-vars="ROLE=${H04_ROLE}" \
      --no-allow-unauthenticated --min=0 --max=1 --memory=512Mi --cpu=1 --timeout=120 --quiet
  gcloud run services add-iam-policy-binding "${H04_SERVICE}" \
    --region="${H04_REGION}" --project="${H04_PROJECT_ID}" \
    --member="serviceAccount:${H04_WORKFLOW_SA}" --role="roles/run.invoker"
done

gcloud storage buckets add-iam-policy-binding "gs://${H04_BUCKET}" \
  --member="serviceAccount:${H04_WORKFLOW_SA}" --role="roles/storage.objectViewer"
gcloud storage buckets add-iam-policy-binding "gs://${H04_BUCKET}" \
  --member="serviceAccount:${H04_WORKFLOW_SA}" --role="roles/storage.objectCreator"
gcloud projects add-iam-policy-binding "${H04_PROJECT_ID}" \
  --member="serviceAccount:${H04_WORKFLOW_SA}" --role="roles/logging.logWriter" \
  --condition=None

H04_MISSION_URL="$(gcloud run services describe spectra-h04-mission --project="${H04_PROJECT_ID}" --region="${H04_REGION}" --format='value(status.url)')"
H04_PARTS_URL="$(gcloud run services describe spectra-h04-parts --project="${H04_PROJECT_ID}" --region="${H04_REGION}" --format='value(status.url)')"
H04_ASSURANCE_URL="$(gcloud run services describe spectra-h04-assurance --project="${H04_PROJECT_ID}" --region="${H04_REGION}" --format='value(status.url)')"

gcloud workflows deploy spectra-h04-e2e \
  --source="${H04_ROOT}/workflow.yaml" --location="${H04_REGION}" \
  --service-account="${H04_WORKFLOW_SA}" --call-log-level=log-errors-only \
  --set-env-vars="MISSION_URL=${H04_MISSION_URL},PARTS_URL=${H04_PARTS_URL},ASSURANCE_URL=${H04_ASSURANCE_URL}" \
  --project="${H04_PROJECT_ID}"

echo "H05 remediation deployment complete: project=${H04_PROJECT_ID} region=${H04_REGION} bucket=${H04_BUCKET}"
