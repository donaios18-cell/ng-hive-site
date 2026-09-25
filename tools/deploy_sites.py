# -*- coding: utf-8 -*-
"""
Выкладка сайтов NG Hive в Cloudflare Pages.

    python tools/deploy_sites.py watch            один сайт
    python tools/deploy_sites.py all              все четыре
    python tools/deploy_sites.py watch --dry-run  показать, что уедет, ничего не выкладывая

Всегда выкладывается свежий коммит из GitHub (origin), а не чья-то рабочая
папка: сайты правят несколько сессий, и выкладка из устаревшей копии молча
откатила бы чужие изменения. Незакоммиченное и неотправленное на сайт не попадёт.

Ключ Cloudflare в репозитории не хранится. Путь к файлу с ключом берётся из
переменной окружения NGHIVE_CF_TOKEN_FILE или из tools/cf-token-path.txt
(файл в .gitignore). В самом файле ключа: строка с ID аккаунта (32 hex-символа)
и строка с токеном.
"""
import io
import os
import re
import shutil
import subprocess
import sys
import tarfile
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(os.path.expanduser("~"), ".nghive-deploy")

SITES = {
    # имя: (репозиторий, ветка, проект Pages, адрес, что не выкладывать)
    "nghive": ("ng-hive-site", "master", "nghive", "https://nghive.app/",
               ("README.md", ".gitignore", ".nojekyll", ".claude/", "posts/", "tools/")),
    "shopping": ("shopping-site", "main", "shopping", "https://shopping.nghive.app/",
                 (".gitignore", ".nojekyll")),
    "watch": ("whatchalarm-site", "main", "whatchalarm", "https://watch.nghive.app/",
              (".gitignore", ".nojekyll")),
    "collage": ("hcollage-site", "main", "collage", "https://collage.nghive.app/",
                (".gitignore", ".nojekyll")),
    "sparrows": ("sparrows-site", "main", "sparrows", "https://sparrows.nghive.app/",
                 (".gitignore", ".nojekyll")),
}


def credentials():
    path = os.environ.get("NGHIVE_CF_TOKEN_FILE")
    if not path:
        cfg = os.path.join(HERE, "cf-token-path.txt")
        if os.path.exists(cfg):
            path = io.open(cfg, encoding="utf-8").read().strip()
    if not path or not os.path.exists(path):
        sys.exit("Не найден файл с ключом Cloudflare: задайте NGHIVE_CF_TOKEN_FILE "
                 "или путь в tools/cf-token-path.txt")
    lines = [l.strip() for l in io.open(path, encoding="utf-8-sig", errors="replace")]
    account = next(l for l in lines if re.fullmatch(r"[0-9a-f]{32}", l))
    token = next(l for l in lines if re.fullmatch(r"[A-Za-z0-9_\-]{35,60}", l))
    return token, account


def git(cwd, *args):
    return subprocess.run(["git", *args], cwd=cwd, check=True,
                          capture_output=True, text=True, encoding="utf-8", errors="replace").stdout.strip()


def fresh_commit(repo, branch):
    """Чистая копия репозитория в служебной папке, подтянутая до origin."""
    os.makedirs(WORK, exist_ok=True)
    path = os.path.join(WORK, repo)
    if not os.path.isdir(os.path.join(path, ".git")):
        subprocess.run(["git", "clone", "-q", "https://github.com/donaios18-cell/%s.git" % repo, path],
                       check=True)
    git(path, "fetch", "-q", "origin", branch)
    ref = "origin/" + branch
    return path, git(path, "rev-parse", "--short", ref), git(path, "log", "-1", "--format=%s", ref), ref


def export(path, ref, skip, dest):
    archive = os.path.join(dest, "_site.tar")
    with open(archive, "wb") as f:
        subprocess.run(["git", "archive", ref], cwd=path, check=True, stdout=f)
    site = os.path.join(dest, "site")
    with tarfile.open(archive) as tar:
        for m in tar.getmembers():
            if any(m.name == s or m.name.startswith(s) for s in skip):
                continue
            tar.extract(m, site)
    os.remove(archive)
    return site


def stamp_assets(site, version):
    """Добавляет ?v=<коммит> к своим css/js в html.

    Cloudflare отдаёт css и js с «хранить 4 часа», а страницу — всегда свежую.
    Без этого посетитель после правки видит новую разметку со старыми стилями.
    """
    pattern = re.compile(r'(?P<attr>href|src)="(?P<url>(?!https?:|//|data:)[^"?#]+\.(?:css|js))"')
    touched = 0
    for dirpath, _, files in os.walk(site):
        for fn in files:
            if not fn.endswith(".html"):
                continue
            path = os.path.join(dirpath, fn)
            text = io.open(path, encoding="utf-8").read()
            new = pattern.sub(lambda m: '%s="%s?v=%s"' % (m.group("attr"), m.group("url"), version), text)
            if new != text:
                io.open(path, "w", encoding="utf-8").write(new)
                touched += 1
    return touched


def deploy(name, dry_run=False):
    repo, branch, project, url, skip = SITES[name]
    path, sha, subject, ref = fresh_commit(repo, branch)
    print("== %s  %s  «%s»" % (name, sha, subject))
    tmp = tempfile.mkdtemp(prefix="nghive-")
    try:
        site = export(path, ref, skip, tmp)
        stamped = stamp_assets(site, sha)
        files = sorted(os.path.relpath(os.path.join(d, f), site).replace("\\", "/")
                       for d, _, fs in os.walk(site) for f in fs)
        if stamped:
            print("   страниц с версией стилей: %d" % stamped)
        print("   файлов: %d" % len(files))
        if dry_run:
            for f in files:
                print("     ", f)
            return
        token, account = credentials()
        env = dict(os.environ, CLOUDFLARE_API_TOKEN=token, CLOUDFLARE_ACCOUNT_ID=account)
        out = subprocess.run(
            "npx --yes wrangler@latest pages deploy \"%s\" --project-name=%s --branch=%s "
            "--commit-hash=%s --commit-message=\"%s\"" % (site, project, branch, sha,
                                                          subject.replace('"', "'")),
            shell=True, env=env, capture_output=True, text=True, encoding="utf-8", errors="replace")
        lines = [l for l in ((out.stdout or "") + (out.stderr or "")).splitlines() if "✨" in l or "ERROR" in l]
        for l in lines:
            print("  ", l.strip())
        if out.returncode != 0:
            sys.exit("   выкладка не удалась")
        print("   живой адрес:", url)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


if __name__ == "__main__":
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    if not args or (args[0] != "all" and args[0] not in SITES):
        sys.exit("укажите сайт: %s или all" % ", ".join(SITES))
    for n in (SITES if args[0] == "all" else [args[0]]):
        deploy(n, dry_run="--dry-run" in sys.argv)
