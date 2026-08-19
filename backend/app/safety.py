"""安全与边界：隐私保护、边界引导、敏感内容拦截。"""
from __future__ import annotations
import re
from dataclasses import dataclass

# ---------- 隐私敏感信息检测（用户输入含这些 → 警告并拦截） ----------
PRIVACY_PATTERNS: list[tuple[str, str]] = [
    (r"\d{17}[\dXx]", "身份证号"),
    (r"\d{4}[ -]?\d{4}[ -]?\d{4}[ -]?\d{4}", "银行卡号"),
    (r"(支付|验证|校验)码[是为：: ]+?\d{4,6}", "支付/验证码"),
]

PRIVACY_WARNING = (
    "⚠️ 温馨提示：请不要在对话中提供身份证号、银行卡号、密码或验证码等敏感信息！"
    "这些信息只应在学校官方系统或线下窗口办理时提供，请立即撤回/删除您刚才的内容。"
    "如需办理校园卡、缴费等业务，请通过学校官方渠道（迎新系统、辅导员）操作。"
)

# ---------- 边界引导（与无锡学院新生无关的通用请求） ----------
# 注意：正则需足够具体，避免误伤校园问题
# （如"不会写作业怎么办"应放行，"帮我写作业"才拦截）
BOUNDARY_PATTERNS: list[tuple[str, str]] = [
    (r"今天(的)?天气|天气预报|气温|会不会下雨", "天气查询"),
    # 写作/翻译/编程代劳：要求出现"写/译"动词且上下文指向创作类请求
    (r"(帮我|请帮我|麻烦帮我).{0,6}写.{0,10}?(作文|文章|小说|诗|诗歌|散文|剧本|代码|程序)", "写作代劳"),
    (r"写(一|两|几)?篇.{0,15}?(作文|文章|小说|诗|诗歌|散文|剧本|代码|程序)", "写作代劳"),
    (r"(帮我|请帮我).{0,6}写.{0,8}(代码|程序|脚本|爬虫|函数|网页)", "编程代劳"),
    (r"写一个.{0,10}(程序|脚本|爬虫|网页|网站|游戏)", "编程代劳"),
    (r"(翻译|译)一下|把.{0,30}?(翻译|译)成.{0,8}(英文|中文|英语|日语|韩语|法语|德语)", "翻译"),
    (r"\d+[+\-*/×÷]\d+.*=|\d+的(平方|立方|阶乘)|解(一下)?(方程|不等式)", "数学计算"),
    (r"(推荐|介绍)(一部|一个)?(电影|电视剧|游戏|歌曲)", "娱乐推荐"),
    (r"股市|股票|彩票|预测(彩票)?号码", "投资/博彩"),
]

BOUNDARY_REPLY = (
    "我是专为无锡学院新生服务的'锡院小智'，请问您有什么关于校园学习或生活的问题吗？"
    "比如报到流程、选课、宿舍、食堂、校园卡、交通路线，我都可以帮您解答哦😊"
)

# ---------- 敏感/违规内容（直接拒绝） ----------
FORBIDDEN_PATTERNS: list[str] = [
    "制作炸药", "自制炸弹", "购买毒品", "合成冰毒", "攻击网站教程",
    "破解银行卡", "盗取账号", "伪造证件",
]
# 涉政等敏感词可按需扩充；正式上线前建议接入云厂商内容安全服务

FORBIDDEN_REPLY = (
    "抱歉，这类问题不在我的服务范围内，我无法回答。"
    "我是专为无锡学院新生提供校园学习与生活帮助的'锡院小智'，请问还有其他校园问题吗？"
)


@dataclass
class CheckResult:
    blocked: bool = False
    reply: str = ""
    reason: str = ""


def check_input(text: str) -> CheckResult:
    """对用户输入做检查，返回是否拦截及拦截回复。"""
    for pattern, name in PRIVACY_PATTERNS:
        if re.search(pattern, text):
            return CheckResult(blocked=True, reply=PRIVACY_WARNING, reason=f"隐私信息:{name}")
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, text):
            return CheckResult(blocked=True, reply=FORBIDDEN_REPLY, reason="违规内容")
    for pattern, name in BOUNDARY_PATTERNS:
        if re.search(pattern, text):
            return CheckResult(blocked=True, reply=BOUNDARY_REPLY, reason=f"边界引导:{name}")
    return CheckResult()


def check_output(text: str, user_input: str) -> str:
    """输出检查：防止模型回显用户曾提供的敏感信息，统一打码。"""
    for pattern, _name in PRIVACY_PATTERNS:
        m = re.search(pattern, user_input)
        if m and re.search(pattern, text):
            # 将回复中与该敏感片段相同的部分打码
            text = re.sub(pattern, "****", text)
    return text
