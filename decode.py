import json
import jwt

encodedStr = "eyJhbGciOiJSUzI1NiIsImtpZCI6ImkzN2QxdXlKSzhtQ3lrSVcxQmZXUmxxUGdRNUtKRm1DUzBQZG1ERTBLZ3cifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJkZWZhdWx0Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZWNyZXQubmFtZSI6InMzdGltZS10b2tlbi1zZ2M3ZiIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VydmljZS1hY2NvdW50Lm5hbWUiOiJzM3RpbWUiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiJiYmQxOTY4Mi04NWViLTQ1ODgtYjE0Zi0zYmI2ODg2NjY0MGQiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6ZGVmYXVsdDpzM3RpbWUifQ.LGIZxcAwcqJHJr00GFzpkGjr_1bGkut7QfZXy4qJ2kG3dV0pvBltmbWQWG9JCP9MJSCedrv0djb19AEQAx76LLil2szd3x7fzwcMQFQGRuDr3z27SFzTBquK5Y4QihgqGXCtWrPPL6DKHFEC33or6V6qhSkFAyI8n0Dr9-8avNJQ1jOI67vtGEWDLmFzBgJ-EJyW2JyAuSHdIHxyj--1kzVUHA5utyx9G7TL93GRMSWLoxk2pMw2PKhyQeuLekDF4dwbA9cMRimyCUSGH8BErbIf6lXV3Hqyx9OGJx0Slv1D7ims5BB79wwU19_T9GVR0xkTFsoI0unRWGU-S8OMlg"

decodedStr = jwt.decode(encodedStr, verify=False, algorithms='RS256')

raw = json.dumps(decodedStr, sort_keys=True, indent=4)

print(raw)