# Using IRSA

This guide assumes an EKS cluster has been provisioned, kubectl has been
configured to communicate to the Kubernetes API server and the inbuilt EKS OIDC
provider has been registered with AWS IAM. If required the following guides can
help:

1) [Create Cluster](https://docs.aws.amazon.com/eks/latest/userguide/create-cluster.html)
2) [Create a Kubeconfig](https://docs.aws.amazon.com/eks/latest/userguide/create-kubeconfig.html)
3) [Enable OIDC Provider](https://docs.aws.amazon.com/eks/latest/userguide/enable-iam-roles-for-service-accounts.html)

Additionally, the demo app container will need to be built and pushed to up to a
container registry.

```bash
$ cd app
$ export ECR=<accountid>.dkr.ecr.<region>.amazonaws.com
$ docker build -t $ECR/s3time:latest .
$ docker push $ECR/s3time:latest
```

## Using a Node Instance Role

If an application deployed within a Kubernetes Pod wants to access external AWS
services, the traditional way to provide the relevant IAM permissions to the
application is through [IAM roles for
EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html).

This guide does not cover how to configure IAM roles for EC2, however this demo
application can be deployed successfully if an IAM role (with an S3 policy) is
attached to the EKS worker nodes. A guide to attaching policies to an IAM role,
and then to attach an IAM role to EKS worker nodes can be found here
[here](https://docs.aws.amazon.com/eks/latest/userguide/worker_node_IAM_role.html).

Once the IAM role has been attached to the EC2 instance, you can deploy the
Kubernetes Pod. 

> Make sure you adjust the S3 Bucket name within the Pod Manifest to something
> that exists within your environment.

```bash
$ kubectl apply -f pod1.yaml
```

You can monitor the pod, and check it is copying data to the bucket succesfully
using `kubectl logs`.

```bash
$ kubectl logs -f s3time
```

Finally, make sure you clean up the pod before starting the IRSA section.

```bash
$ kubectl delete pod s3time
```

## Using IAM roles for Service Accounts

One of the main draw backs of using [IAM roles for
EC2](https://docs.aws.amazon.com/AWSEC2/latest/UserGuide/iam-roles-for-amazon-ec2.html)
with an EKS worker node, is that all pods running on the EKS worker node will be
given the same permissions. If 2 Kubernetes pods were deployed on to the same
EKS worker node, and 1 pod required access to an S3 bucket, you would be unable
to apply granular permissions. Both Kubernetes Pods would have access to the S3
bucket.

Additionally, Kubernetes Pod are passed an identity through the form a
Kubernetes Service Account. This identity is traditionally used to apply
permissions within a Kubernetes cluster, specifically to the Kubernetes API
server, however using [IAM roles for Service Accounts
(IRSA)](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts.html).
a Kubernetes service account can also be a recognised identity outside of the
Kubernetes cluster.

### Create the Role

When using IRSA, an IAM role needs to be pre-created within the AWS account.
This role links the Kubernetes Service Account's identity from the OIDC provider
with an IAM policy.

The provided `trust.json` will need to be modified for each environment. The
namespace and the service account need to be specified in this trust document,
as well as the OIDC provider's address. The Kubernetes serivce account does not
need to exist at this time. 

The OIDC provider address can be obtained with:

```bash
OIDC_PROVIDER=$(aws eks describe-cluster --name cluster-name --query "cluster.identity.oidc.issuer" --output text | sed -e "s/^https:\/\///")
```

Using the `trust.json` file create an IAM role. Then attach an IAM policy to
this role. In this example we have attached the managed `AmazonS3FullAccess`
role (this is out of laziness), a more granular role with just permissions to a
single S3 bucket would be the recommended route.

```bash
aws iam create-role \
  --role-name s3timearn \
  --assume-role-policy-document file://trust.json \
  --description "S3 time Role"

aws iam attach-role-policy \
  --role-name s3timearn \
  --policy-arn=arn:aws:iam::aws:policy/AmazonS3FullAccess
```

### Deploy the Workload

Now IAM is configured to respond to a Kubernetes Service Account identity, we
will need to create that Service Account within Kubernetes.

> Note you will need to patch the `sa.yaml` with the arn of the role you have
> just created*.

```bash
kubectl apply -f sa.yaml
```

We can now deploy the workload. `pod2.yaml` differs from `pod1.yaml` by a
defined Service Account to run within the pod. If `serviceAccount` is not
defined within the pod specification, as is the case with `pod1.yaml` the
namespace's default Service Account is used. `pod2.yaml` includes
`serviceAccount: s3time` telling the pod to consume the newly created `s3time`
Service Account.

> Make sure you adjust the S3 Bucket name within the Pod Manifest to something
> that exists within your environment.

```bash
kubectl apply -f pod2.yaml
```

You can monitor the pod, and check it is copying data to the bucket succesfully
using `kubectl logs`.

```bash
$ kubectl logs -f s3time
```

### Under the Hood

Under the hood, when a Service Account is annotated with a role-arn, An STS
token is injected via the [EKS Pod
Identity](https://github.com/aws/amazon-eks-pod-identity-webhook) webhook.

You can see this has been succesfully added if you compare a pod running from
`pod1.yaml` with a pod running from `pod2.yaml`.

#### Without IRSA

```bash
$ kubectl exec -it s3time bash
root@s3time:/app# env | grep AWS

$ ls -l /var/run/secrets/
total 0
drwxr-xr-x 3 root root 28 Jul 17 15:41 kubernetes.io

$ ls -l /var/run/secrets/kubernetes.io/
total 0
drwxrwxrwt 3 root root 140 Jul 17 15:41 serviceaccount

$ ls -l /var/run/secrets/kubernetes.io/serviceaccount/
total 0
lrwxrwxrwx 1 root root 13 Jul 17 15:41 ca.crt -> ..data/ca.crt
lrwxrwxrwx 1 root root 16 Jul 17 15:41 namespace -> ..data/namespace
lrwxrwxrwx 1 root root 12 Jul 17 15:41 token -> ..data/token
```

#### With IRSA 

```bash
$ env | grep AWS
AWS_ROLE_ARN=arn:aws:iam::223615444511:role/s3timearn
AWS_WEB_IDENTITY_TOKEN_FILE=/var/run/secrets/eks.amazonaws.com/serviceaccount/token

$ ls -l /var/run/secrets/
total 0
drwxr-xr-x 3 root root 28 Jul 17 15:44 eks.amazonaws.com
drwxr-xr-x 3 root root 28 Jul 17 15:44 kubernetes.io

$ ls -l /var/run/secrets/eks.amazonaws.com/serviceaccount/
total 0
lrwxrwxrwx 1 root root 12 Jul 17 15:44 token -> ..data/token
```

Modern versions of the SDK will automatically look for the AWS environment
variables and respect them as way to authenticate with AWS, as can be seen
[here](https://github.com/boto/boto3/blob/master/docs/source/guide/credentials.rst#assume-role-with-web-identity-provider)
in the python SDK. The list of supported SDKs can be found
[here](https://docs.aws.amazon.com/eks/latest/userguide/iam-roles-for-service-accounts-minimum-sdk.html).
This means a developer does not need to change their application code to take
advantage of IRSA. They just need to make sure they are running a modern version
of the SDK.

If you wanted to decode the STS JWT token the Webhook has placed into the pod,
you could do so using the `pyjwt` python module. For comparison here, I have
also decoded the Kubernetes Service Account token.

Note if the token has been mounted in a pod, it has already been base64 decoded.
If you are taking a Kubernetes Service Account token from the Kubernetes API
server (e.g. `kubectl get secret <sa-token> -o jsonpath='{.data.token}'`) it
will be base64 encoded, and need to be decoded first.

This sample script will decode a JWT for you.

```python
import json
import jwt

encodedStr = "<string>"

decodedStr = jwt.decode(encodedStr, verify=False, algorithms='RS256')

raw = json.dumps(decodedStr, sort_keys=True, indent=4)

print(raw)
```

##### STS JWT Token

The STS token that can be found at
`/var/run/secrets/eks.amazonaws.com/serviceaccount/token` once decoded through
the sample script above, becomes:

```json
{
    "aud": [
        "sts.amazonaws.com"
    ],
    "exp": 1595087063,
    "iat": 1595000663,
    "iss": "https://oidc.eks.eu-west-1.amazonaws.com/id/<url>",
    "kubernetes.io": {
        "namespace": "default",
        "pod": {
            "name": "s3time",
            "uid": "9ae52fb8-3ec0-4b84-afc3-e07f1832774d"
        },
        "serviceaccount": {
            "name": "s3time",
            "uid": "bbd19682-85eb-4588-b14f-3bb68866640d"
        }
    },
    "nbf": 1595000663,
    "sub": "system:serviceaccount:default:s3time"
}
```

##### Kubernetes SA JWT Token

The Kubernetes Service Account Token that can be found at
`/var/run/secrets/kubernetes.io/serviceaccount/token`, once decoded through the
sample script above, becomes:


Becomes:

```json
{
    "iss": "kubernetes/serviceaccount",
    "kubernetes.io/serviceaccount/namespace": "default",
    "kubernetes.io/serviceaccount/secret.name": "s3time-token-sgc7f",
    "kubernetes.io/serviceaccount/service-account.name": "s3time",
    "kubernetes.io/serviceaccount/service-account.uid": "bbd19682-85eb-4588-b14f-3bb68866640d",
    "sub": "system:serviceaccount:default:s3time"
}
```