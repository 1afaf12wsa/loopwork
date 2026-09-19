# Deploying the site

The site runs as a **Cloudflare Worker with static assets**. Everything in
`public/` is served from Cloudflare's edge without running any code. The worker
in `worker.js` wakes only for the signup form, so there is nothing to pay for
and nothing to wake up.

## Why not Render

Render runs one machine in one region. On the free plan it sleeps after about
15 minutes idle, and a visitor pays 30 to 60 seconds for the wake up. Pages has
no origin to wake, serves from the city nearest the visitor, and does not care
how much traffic a creator's launch post sends at once.

## One time setup in the Cloudflare dashboard

1. **Workers & Pages** → **Create** → **Import a repository** → pick .
2. Project name , build command **empty**, deploy command
   
╭─────────────────────────────────╮
│ Did you mean "wrangler deploy"? │
╰─────────────────────────────────╯

wrangler

COMMANDS
  wrangler docs [search..]        📚 Open Wrangler's command documentation in your browser
  wrangler complete [shell]       ⌨️ Generate and handle shell completions

  wrangler email                  Manage Cloudflare Email services [open beta]

ACCOUNT
  wrangler auth                   🔐 Manage authentication
  wrangler login                  🔓 Login to Cloudflare
  wrangler logout                 🚪 Logout from Cloudflare
  wrangler whoami                 🕵️ Retrieve your user information

COMPUTE & AI
  wrangler agent-memory           🧠 Manage Agent Memory namespaces [private beta]
  wrangler ai                     🤖 Manage AI models
  wrangler ai-search              🔍 Manage AI Search instances [open beta]
  wrangler browser                🌐 Manage Browser Run sessions [open beta]
  wrangler containers             📦 Manage Containers
  wrangler delete [name]          🗑️ Delete a Worker from Cloudflare
  wrangler deploy [path]          🆙 Deploy a Worker to Cloudflare
  wrangler deployments            🚢 List and view the current and past deployments for your Worker
  wrangler dev [script]           👂 Start a local server for developing your Worker
  wrangler dispatch-namespace     🏗️ Manage dispatch namespaces
  wrangler flagship               🚩 Manage Flagship apps and feature flags [open beta]
  wrangler init [name]            📥 Initialize a basic Worker
  wrangler pages                  ⚡️ Configure Cloudflare Pages
  wrangler preview [script]       👀 Create a Preview deployment of the current Worker [open beta]
  wrangler queues                 📬 Manage Workers Queues
  wrangler rollback [version-id]  🔙 Rollback a deployment for a Worker
  wrangler secret                 🤫 Generate a secret that can be referenced in a Worker
  wrangler setup                  🪄 Setup a project to work on Cloudflare
  wrangler tail [worker]          🦚 Start a log tailing session for a Worker
  wrangler triggers               🎯 Updates the triggers of your current deployment [experimental]
  wrangler types [path]           📝 Generate types from your Worker configuration
  wrangler versions               🫧 List, view, upload and deploy Versions of your Worker to Cloudflare
  wrangler vpc                    🌐 Manage VPC [open beta]
  wrangler workflows              🔁 Manage Workflows

STORAGE & DATABASES
  wrangler artifacts              🧱 Manage Artifacts namespaces and repos [private beta]
  wrangler d1                     🗄️ Manage Workers D1 databases
  wrangler hyperdrive             🚀 Manage Hyperdrive databases
  wrangler kv                     🗂️ Manage Workers KV Namespaces
  wrangler pipelines              🚰 Manage Cloudflare Pipelines [open beta]
  wrangler r2                     📦 Manage R2 buckets & objects
  wrangler secrets-store          🔐 Manage the Secrets Store [open beta]
  wrangler vectorize              🧮 Manage Vectorize indexes

NETWORKING & SECURITY
  wrangler cert                   🪪 Manage client mTLS certificates and CA certificate chains used for secured connections [open beta]
  wrangler mtls-certificate       🪪 Manage certificates used for mTLS connections
  wrangler tunnel                 🚇 Manage Cloudflare Tunnels [experimental]
  wrangler turnstile              🛡️ Manage Turnstile widgets [alpha]

GLOBAL FLAGS
  -c, --config          Path to Wrangler configuration file  [string]
      --cwd             Run as if Wrangler was started in the specified directory instead of the current working directory  [string]
  -e, --env             Environment to use for operations, and for selecting .env and .dev.vars files  [string]
      --env-file        Path to an .env file to load - can be specified multiple times - values from earlier files are overridden by values in later files  [array]
  -h, --help            Show help  [boolean]
      --install-skills  Install Cloudflare skills for detected AI coding agents before running the command  [boolean] [default: false]
      --profile         Use a specific auth profile  [string]
  -v, --version         Show version number  [boolean]

Please report any issues to https://github.com/cloudflare/workers-sdk/issues/new/choose. Everything else comes from .
3. **Deploy**, then open the  URL it gives you and check the site.
4. **Settings → Variables and Secrets** → add secret  from
   resend.com. Redeploy afterwards, secrets only reach new deployments.
5. **Settings → Domains & Routes** → add  and . This is
   the moment traffic leaves Render.

 and  live in , not the dashboard,
because a deploy would overwrite dashboard values.

### Optional: duplicate detection

Create a KV namespace, then add its id to  under
 and redeploy. Without it the form still works, it just cannot
tell a repeat signup from a new one.

## Why Resend rather than Gmail

Workers cannot open raw TCP connections, so SMTP is impossible. Email has to go
out over an HTTP API. Resend's free tier is 3,000 a month, far beyond what this
form will ever do.

## What stayed behind

`server.js` still holds the Twilio missed call webhooks from the earlier agent
product. They are not deployed anywhere. If a real phone number is ever pointed
at them again they need porting to Functions first, including the signature
check, which uses HMAC SHA1 and works fine with Web Crypto.

## Local preview

`npx wrangler pages dev public` runs the pages and the Functions together.
