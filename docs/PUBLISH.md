# GitHub发布 / Publishing to GitHub

在完整基地运行Export-OpenSource.ps1，指定一个全新目录。检查生成的源码清单和ZIP，进入导出的目录初始化公开历史。

Run Export-OpenSource.ps1 from the full workspace with a fresh destination. Inspect the source manifest and ZIP, then initialize the public history in the exported directory.

```powershell
.\Export-OpenSource.ps1 -Destination C:\work\Nyquest_AI_Lab_Public
Set-Location C:\work\Nyquest_AI_Lab_Public
git init -b main
git add .
git commit -m 'Initial public source release'
```

在自己的GitHub账号创建空仓库，将实际地址用于下列命令。

Create an empty repository in your own GitHub account and use its actual URL below.

```powershell
git remote add origin <your-GitHub-repository-URL>
git push -u origin main
```

公开目录包含README中英文、MIT授权、自主脚本、示例源码配方、测试与CI。厂商组件由每位使用者通过Setup从自己的安装目录导入。源码清单按文件记录SHA256，ZIP经过CRC与逐文件哈希核验。

The public tree contains Chinese/English README files, MIT licensing, project-authored scripts, example source recipes, tests and CI. Each user imports vendor components from their own installation through Setup. The source manifest records each file's SHA256; the ZIP receives CRC and per-file hash verification.
