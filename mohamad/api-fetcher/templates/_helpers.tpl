{{/*
Return the chart name
*/}}
{{- define "api-fetcher.name" -}}
{{- default .Chart.Name .Values.nameOverride }}
{{- end }}

{{/*
Return the fully qualified app name
*/}}
{{- define "api-fetcher.fullname" -}}
{{- if .Values.fullnameOverride }}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" }}
{{- else }}
{{- $name := default .Chart.Name .Values.nameOverride }}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" }}
{{- end }}
{{- end }}

{{/*
Common labels
*/}}
{{- define "api-fetcher.labels" -}}
app.kubernetes.io/name: {{ include "api-fetcher.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end }}

{{/*
Selector labels
*/}}
{{- define "api-fetcher.selectorLabels" -}}
app.kubernetes.io/name: {{ include "api-fetcher.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end }}

{{/*
Return the service account name
*/}}
{{- define "api-fetcher.serviceAccountName" -}}
{{- if .Values.serviceAccount.name }}
{{- .Values.serviceAccount.name }}
{{- else }}
{{- include "api-fetcher.fullname" . }}
{{- end }}
{{- end }}
