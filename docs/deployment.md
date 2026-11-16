# Deployment (Week 5)

Team: T Triple A

| | |
|---|---|
| Service URL | https://credit-risk-api-685424255950.us-central1.run.app |
| Project id / region | credit-risk-ttriplea / us-central1 |
| Image | us-central1-docker.pkg.dev/credit-risk-ttriplea/credit-risk/api:v1 |
| Model bucket | gs://credit-risk-models-credit-risk-ttriplea (private: public access prevention enforced, uniform access) |
| Model version served | credit-risk version 1 (`models:/credit-risk@staging`, threshold 0.075, validation AUC 0.722) |
| Instances | min 0, max 2 |
| Memory / CPU | 1 GiB / 1 vCPU |
| Service account | credit-risk-api@credit-risk-ttriplea.iam.gserviceaccount.com; role: Storage Object Viewer on the model bucket only |

The service downloads `model.joblib`, `model_info.json` and `feature_store.parquet` from the
bucket when it starts (`MODEL_BUCKET=gs://credit-risk-models-credit-risk-ttriplea`), so the image
holds only the code and its pinned packages. It runs as a non-root user, and anyone can call it
(`--allow-unauthenticated`), since this is a course demo with no real customers.

Checked after the deploy: `/health` returned `model_loaded: true`, `/predict` for applicant
100021 returned probability 0.0753 and `reject` (at or above the 0.075 threshold), and an unknown
id returned 404.

Note on the build: `docker build` in Cloud Shell stalled while downloading the base image from
Docker Hub (the network there was very slow that day), so the image was built and pushed with
Cloud Build instead (`gcloud builds submit --tag $IMAGE .`), from the same Dockerfile. Cloud Build
runs as the project's default compute service account, which we gave only: Storage Object Viewer
on the `credit-risk-ttriplea_cloudbuild` staging bucket, Artifact Registry Writer on the
`credit-risk` repository, and Logs Writer on the project.

## How to deploy a new model

1. Register the new model (`python run.py final`), then `python run.py export`. This rewrites the
   three files in `models/` and `requirements-api.txt`.
2. If `requirements-api.txt` changed, commit it on a branch and merge it through a pull request
   (and keep the Dockerfile's `FROM` on the same Python minor version as its second line).
3. Upload the three `models/` files to the **top level** of
   `gs://credit-risk-models-credit-risk-ttriplea`, replacing the old ones (Console: the bucket →
   Upload files, or `gcloud storage cp models/* gs://credit-risk-models-credit-risk-ttriplea/`).
4. In Cloud Shell, set the variables from step 0 of `docs/deploy_cloud_run.md`, then:
   - if the code or the requirements changed: clone main again and rebuild the image with
     `gcloud builds submit --tag $IMAGE .`;
   - roll out a new revision so the service downloads the new bundle on start-up (it only reads
     the bucket when it starts): run the same `gcloud run deploy credit-risk-api ...` command from
     step 8 of the checklist.
5. Check `curl $URL/model-info` shows the new version and threshold, then call `/predict` once
   with an id from the new feature store.
6. Update the "Model version served" row above, and run `python run.py check`.
