import os
from github import Github
from datetime import datetime, timedelta

# 初始化GitHub API
g = Github(os.environ['GITHUB_TOKEN'])
repo = g.get_repo(os.environ['GITHUB_REPOSITORY'])

# 获取所有贡献者
contributors = set(c.login for c in repo.get_contributors())

# 定义日期范围（从6月24日到7月14日）
start_date = datetime(2024, 6, 24)
end_date = datetime(2024, 7, 14)
date_range = [(start_date + timedelta(days=x)).strftime("%m.%d") for x in range((end_date - start_date).days + 1)]

# 获取每个用户在每一天的提交状态
user_commits = {user: {} for user in contributors}
for date in date_range:
    day = datetime.strptime(date, "%m.%d").replace(year=2024)
    next_day = day + timedelta(days=1)
    commits = repo.get_commits(since=day, until=next_day)
    for commit in commits:
        if commit.author:
            user_commits[commit.author.login][date] = "✅"

# 检查是否有人在一周内超过两天没有提交
def check_elimination(user_commits, user, date):
    week_dates = [date]
    current_date = datetime.strptime(date, "%m.%d").replace(year=2024).date()
    for i in range(1, 7):
        prev_date = (current_date - timedelta(days=i)).strftime("%m.%d")
        if prev_date in date_range:
            week_dates.append(prev_date)
    
    missing_days = sum(1 for d in week_dates if user_commits[user].get(d, "⭕️") == "⭕️")
    return missing_days > 2

# 生成新的表格内容
new_table = ['| EICL1st· Name | ' + ' | '.join(date_range) + ' |\n',
             '| ------------- | ' + ' | '.join(['----' for _ in date_range]) + ' |\n']

for user in contributors:
    row = f"| {user} |"
    eliminated = False
    for date in date_range:
        if eliminated:
            status = "❌"
        else:
            status = user_commits[user].get(date, "⭕️")
            if status == "⭕️" and check_elimination(user_commits, user, date):
                eliminated = True
                status = "❌"
        row += f" {status} |"
    new_table.append(row + '\n')

# 读取README.md文件
with open('README.md', 'r') as file:
    content = file.read()

# 查找标记并替换内容
start_marker = "<!-- START_COMMIT_TABLE -->"
end_marker = "<!-- END_COMMIT_TABLE -->"
start_index = content.find(start_marker)
end_index = content.find(end_marker)

if start_index != -1 and end_index != -1:
    new_content = (
        content[:start_index + len(start_marker)] + 
        '\n' + ''.join(new_table) + '\n' + 
        content[end_index:]
    )
    
    # 写入更新后的内容
    with open('README.md', 'w') as file:
        file.write(new_content)
else:
    print("Error: Couldn't find the table markers in README.md")