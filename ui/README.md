# Learn PostgreSQL Antora UI

This directory contains the local Antora UI bundle. The source is split between
Handlebars partials, semantic CSS, and vanilla JavaScript reader enhancements.

Build the bundle with:

```sh
./ui/build-ui.sh
```

The generated `ui/build/ui-bundle.zip` is consumed by
`playbook/antora-playbook.yml`.
