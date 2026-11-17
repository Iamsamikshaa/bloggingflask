import express from "express";
import type { Request, Response } from "express";
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { spawn, execFile } from "node:child_process";
import type { ChildProcess } from "node:child_process";

const PORT = 3000;
const FLASK_HOST = "127.0.0.1";
const FLASK_PORT = 5001;
const ROOT_DIR = process.cwd();
const FLASK_DIR = path.join(ROOT_DIR, "flask-blog-management-system");
const VENV_PYTHON = "/tmp/flask-venv/bin/python";
const ZIP_OUTPUT = "/tmp/flask-blog-management-system.zip";

let flaskProcess: ChildProcess | null = null;

function getPythonExecutable(): string {
  return fs.existsSync(VENV_PYTHON) ? VENV_PYTHON : "python3";
}

function startFlaskServer(): void {
  const pythonBin = getPythonExecutable();
  flaskProcess = spawn(pythonBin, ["run.py"], {
    cwd: FLASK_DIR,
    env: {
      ...process.env,
      PORT: String(FLASK_PORT),
      FLASK_CONFIG: process.env.FLASK_CONFIG || "development",
      ENABLE_ZIP_DOWNLOAD: "true",
      PYTHONUNBUFFERED: "1",
    },
    stdio: ["ignore", "pipe", "pipe"],
  });

  flaskProcess.stdout?.on("data", (chunk: Buffer) => {
    process.stdout.write(`[flask] ${chunk.toString()}`);
  });

  flaskProcess.stderr?.on("data", (chunk: Buffer) => {
    process.stderr.write(`[flask] ${chunk.toString()}`);
  });

  flaskProcess.on("exit", (code) => {
    console.error(`[flask] process exited with code ${code}`);
    flaskProcess = null;
  });
}

function checkFlaskReady(): Promise<boolean> {
  return new Promise((resolve) => {
    const req = http.get(
      { host: FLASK_HOST, port: FLASK_PORT, path: "/about", timeout: 1000 },
      (res) => {
        res.resume();
        resolve(true);
      }
    );
    req.on("error", () => resolve(false));
    req.on("timeout", () => {
      req.destroy();
      resolve(false);
    });
  });
}

async function waitForFlask(maxWaitMs = 8000): Promise<boolean> {
  const start = Date.now();
  while (Date.now() - start < maxWaitMs) {
    if (await checkFlaskReady()) {
      return true;
    }
    await new Promise((r) => setTimeout(r, 200));
  }
  return false;
}

function buildProjectZip(): Promise<string> {
  const pyScript = `
import os, zipfile

root = ${JSON.stringify(FLASK_DIR)}
out_zip = ${JSON.stringify(ZIP_OUTPUT)}
exclude_dirs = {"__pycache__", ".pytest_cache", ".venv", "venv", "instance", ".git"}
exclude_files = {".env", ".DS_Store"}

with zipfile.ZipFile(out_zip, "w", zipfile.ZIP_DEFLATED) as zf:
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in exclude_dirs]
        rel_dir = os.path.relpath(dirpath, root)
        for fname in filenames:
            if fname in exclude_files or fname.endswith((".pyc", ".pyo", ".db", ".sqlite", ".sqlite3")):
                continue
            if rel_dir.replace("\\\\", "/").endswith("app/static/uploads") and fname != ".gitkeep":
                continue
            full_path = os.path.join(dirpath, fname)
            arc_name = os.path.join("flask-blog-management-system", os.path.relpath(full_path, root))
            zf.write(full_path, arc_name)
`;
  return new Promise((resolve, reject) => {
    execFile(getPythonExecutable(), ["-c", pyScript], (err) => {
      if (err) {
        reject(err);
      } else {
        resolve(ZIP_OUTPUT);
      }
    });
  });
}

function rewriteSetCookieForIframe(
  cookies: string | string[] | undefined,
  isHttpsProxy: boolean
): string[] | undefined {
  if (!cookies) return undefined;
  const list = Array.isArray(cookies) ? cookies : [cookies];
  if (!isHttpsProxy) {
    return list;
  }
  return list.map((cookieStr) => {
    let updated = cookieStr.replace(/;\s*SameSite=Lax/gi, "");
    if (!/;\s*SameSite=None/i.test(updated)) {
      updated += "; SameSite=None";
    }
    if (!/;\s*Secure/i.test(updated)) {
      updated += "; Secure";
    }
    return updated;
  });
}

async function main() {
  startFlaskServer();
  await waitForFlask(6000);

  const app = express();

  app.get("/download/flask-blog-management-system.zip", async (_req: Request, res: Response) => {
    try {
      const zipPath = await buildProjectZip();
      res.download(zipPath, "flask-blog-management-system.zip");
    } catch (err) {
      console.error("ZIP build failed:", err);
      res.status(500).send("Unable to build project archive.");
    }
  });

  app.use(async (req: Request, res: Response) => {
    const ready = await waitForFlask(3000);
    if (!ready) {
      res.status(503).send("Flask server is starting, please refresh in a moment.");
      return;
    }

    const fwdProto = req.headers["x-forwarded-proto"];
    const isHttpsProxy =
      typeof fwdProto === "string" && fwdProto.split(",")[0].trim().toLowerCase() === "https";

    const proxyHeaders: http.OutgoingHttpHeaders = {
      ...req.headers,
      host: req.headers.host || `${FLASK_HOST}:${FLASK_PORT}`,
      "x-forwarded-host": req.headers.host || `${FLASK_HOST}:${FLASK_PORT}`,
      "x-forwarded-proto": isHttpsProxy ? "https" : "http",
    };

    const proxyReq = http.request(
      {
        host: FLASK_HOST,
        port: FLASK_PORT,
        path: req.originalUrl,
        method: req.method,
        headers: proxyHeaders,
      },
      (proxyRes) => {
        const responseHeaders: http.OutgoingHttpHeaders = { ...proxyRes.headers };
        if (responseHeaders["set-cookie"]) {
          responseHeaders["set-cookie"] = rewriteSetCookieForIframe(
            responseHeaders["set-cookie"],
            isHttpsProxy
          );
        }
        res.writeHead(proxyRes.statusCode || 502, responseHeaders);
        proxyRes.pipe(res);
      }
    );

    proxyReq.on("error", (err) => {
      console.error("Proxy error:", err);
      if (!res.headersSent) {
        res.status(502).send("Upstream Flask application unavailable.");
      }
    });

    req.pipe(proxyReq);
  });

  const server = app.listen(PORT, "0.0.0.0", () => {
    console.log(`FolioPress server listening on http://0.0.0.0:${PORT} -> Flask :${FLASK_PORT}`);
  });

  const shutdown = () => {
    server.close();
    if (flaskProcess && !flaskProcess.killed) {
      flaskProcess.kill("SIGTERM");
    }
    process.exit(0);
  };

  process.on("SIGINT", shutdown);
  process.on("SIGTERM", shutdown);
}

main();
