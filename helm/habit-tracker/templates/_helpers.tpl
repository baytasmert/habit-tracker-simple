{{/*
Common labels
*/}}
{{- define "habit-tracker.labels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app.kubernetes.io/version: {{ .Chart.AppVersion }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
helm.sh/chart: {{ .Chart.Name }}-{{ .Chart.Version }}
{{- end }}

{{/*
Selector labels for a component
*/}}
{{- define "habit-tracker.selectorLabels" -}}
app.kubernetes.io/name: {{ .Chart.Name }}
app: {{ . }}
{{- end }}
