git init              # 初始化本地仓库
git remote add origin 仓库地址  # 关联 GitHub
git remote -v         # 查看关联的远程地址

git add .             # 添加所有修改
git commit -m "说明"  # 保存版本
git push              # 上传到 GitHub

git status            # 查看当前文件状态
git log               # 查看提交历史

git pull              # 拉取最新代码

git restore 文件名     # 撤销某个文件的修改
git rm --cached -r 文件夹  # 取消Git追踪（比如config）

git branch            # 查看当前分支
git branch 新分支名    # 创建分支
git checkout 分支名    # 切换分支

# 更新代码
git add .
git commit -m "更新内容"
git pull      # 拉取最新代码
git push     # 上传到 GitHub 

git config --global http.timeout 600     # 设置超时时间，解决 408 错误
git config --global --unset http.timeout  # 取消设置超时时间


# mkdocs 相关命令
mkdocs serve  # 启动本地服务器
mkdocs build   # 构建文档
mkdocs gh-deploy  # 部署到 GitHub Pages
mkdocs new my-project  # 创建新项目
mkdocs build --clean  # 清理旧文件并构建



git push origin gh-pages --force

