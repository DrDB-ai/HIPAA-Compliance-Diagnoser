# Deploying to AWS (ECS), GCP (Cloud Run), and Azure (ACI)

### Deploying to AWS

1. **Sign in to AWS Console:**
   Log in to your AWS Management Console.

2. **Navigate to ECS Service:**
   Go to the Amazon ECS service.

3. **Create a New Task Definition:**
   Click on "Task Definitions" and then "Create new Task Definition". Select "Fargate" launch type and configure your task definition settings.

4. **Configure Container Settings:**
   Add a container to your task definition and specify the Docker image "ghcr.io/drdb-ai/hipaa-compliance-diagnoser". Configure container settings such as port mappings and environment variables.

5. **Create a Cluster:**
   If you haven't already, create an ECS cluster to run your task.

6. **Create a Service:**
   Create a new service using your task definition and configure the desired service settings.

7. **Deploy the Service:**
   Once configured, deploy your service to start running the Docker container on AWS Fargate.

8. **Access Your Application:**
   After deployment, your application will be accessible via the public IP address or domain name associated with your AWS Fargate service.

### Deploying to GCP

1. **Sign in to GCP Console:**
   Log in to your Google Cloud Console.

2. **Navigate to Cloud Run:**
   Go to the Cloud Run section of the console.

3. **Create a New Service:**
   Click on "Create Service" to create a new Cloud Run service.

4. **Specify Service Configuration:**
   Fill in the required details such as the service name, region, and deployment platform (fully managed or Anthos). Select the Docker image "ghcr.io/drdb-ai/hipaa-compliance-diagnoser" from the container image URL.

5. **Configure Additional Settings:**
   Configure any additional settings such as CPU, memory, maximum instances, and concurrency.

6. **Deploy the Service:**
   Once configured, click on "Deploy" to deploy the Cloud Run service.

7. **Access Your Application:**
   After deployment, your application will be accessible via the URL provided by Cloud Run. You can also map a custom domain if needed.

### Deploying to Azure

1. **Sign in to Azure Portal:**
   Log in to the Azure Portal.

2. **Navigate to Azure Container Instances (ACI):**
   Go to the Container Instances section of the portal.

3. **Create a New Container Instance:**
   Click on "Create" to create a new container instance.

4. **Specify Container Details:**
   Provide details such as container image "ghcr.io/drdb-ai/hipaa-compliance-diagnoser", resource group, and other settings.

5. **Deploy the Container:**
   Once configured, deploy the container instance.

6. **Access Your Application:**
   After deployment, your application will be accessible via the public IP address associated with the Azure Container Instance.
