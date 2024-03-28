PROJECT=blank-gpt

# gcloud builds submit --project=$PROJECT --tag europe-docker.pkg.dev/$PROJECT/elo-match/elo-match-image . 

gcloud run deploy elo-match \
  --image europe-docker.pkg.dev/blank-gpt/elo-match/elo-match-image \
  --platform managed \
  --region europe-west1 
  --allow-unauthenticated \
  --service-account=elo-match-cloud-run@$PROJECT.iam.gserviceaccount.com

