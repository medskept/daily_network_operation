# Daily network operation

## Run Artifactoy
GO TO : https://artifactory.defard.org/<br />
Default creds : admin/password

## Run SonarQube
GO TO : https://sonar.defard.org/<br />
Default creds : admin/admin

## HOW-TO set up

Kubernetes version : v1.16.x<br />
Sonarqube version : v8.2-community<br />
Artifactory version : v7.7.3 OSS<br />
Cert-manager version : v0.16.1<br />
Nginx version : v0.29.0<br />

### Step 1 - Deploy the NGINX Ingress Controller

Create a static ip

```
az network public-ip create --resource-group MC_Almond_support_francecentral --name supportStaticIP --sku Standard --allocation-method static --query publicIp.ipAddress -o tsv
```

```
kubectl create namespace nginx-ingress

helm repo add stable https://kubernetes-charts.storage.googleapis.com
helm repo update
helm install nginx-ingress stable/nginx-ingress --namespace nginx-ingress
OR
helm install ingress stable/nginx-ingress --namespace nginx-ingress --set controller.service.loadBalancerIP="STATIC_IP" 
```

### Step 2 - Deploy your appplications

Deploy Artifactory

```
kubectl create namespace artifactory

helm repo add center https://repo.chartcenter.io
helm repo update

helm upgrade --install artifactory --set ingress.enabled=false --set nginx.enabled=false --set postgresql.enabled=true --set artifactory.image.repository=docker.bintray.io/jfrog/artifactory-oss --version 10.1.0 --namespace test center/jfrog/artifactory
```

Deploy Sonarqube

```
kubectl create namespace sonarqube

kubectl apply -f postgres.yaml
kubectl apply -f sonarqube.yaml
```

** You should test your application connexion with the port-forward before exposing them to the internet **

### Step 3 - Deploy Cert-manager

```
kubectl create namespace cert-manager

helm repo add jetstack https://charts.jetstack.io
helm repo update
kubectl apply --validate=false -f https://github.com/jetstack/cert-manager/releases/download/v0.16.1/cert-manager.crds.yaml

helm install cert-manager jetstack/cert-manager --namespace cert-manager --version v0.16.1
```

** Make sure you don't have any file conf from a previous version already installed ! **

### Step 4 - Configure Let's Encrypt Issuer & Deploy a TLS ingress ressource

Create a cluster issuer in the default namespace

```
kubectl apply -f prod-issuer.yaml
```

Create an ingress ressource in the same namespace of the application

```
kubectl apply -f ingress-artifactory.yaml
kubectl apply -f ingress-sonar.yaml
```

### Step 5 - Deploy Backups
Artifactory:
```
kubectl create secret docker-registry acr-secret \
    --namespace artifactory \
    --docker-server=almondregistry.azurecr.io \
    --docker-username=2cc47abc-2297-47f0-8268-02f44aa3e27e \
    --docker-password=1f754f71-cd1f-4946-a868-a9f0633c8f28

```
```
kubectl apply -f backup/artifactory-backup-cronJob.yaml 
```
Sonarqube : 
```
kubectl create secret docker-registry acr-secret \
    --namespace sonarqube \
    --docker-server=almondregistry.azurecr.io \
    --docker-username=2cc47abc-2297-47f0-8268-02f44aa3e27e \
    --docker-password=1f754f71-cd1f-4946-a868-a9f0633c8f28

```
```
kubectl apply -f backup/pod-reader
```
```
kubectl apply -f backup/sonar-backup-cronJob.yaml 
```
