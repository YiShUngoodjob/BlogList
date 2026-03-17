import json
import random
import string

def generate_invite_codes(count=20):
    """生成邀请码"""
    codes = []
    for _ in range(count):
        random_part = ''.join(random.choices(string.digits, k=6))
        code = f"wysVIP{random_part}"
        codes.append(code)
    return codes

# 生成20条邀请码
codes = generate_invite_codes(20)

# 保存到JSON文件
with open('vipcode.json', 'w', encoding='utf-8') as f:
    json.dump(codes, f, ensure_ascii=False, indent=2)

print("生成的邀请码:")
for code in codes:
    print(code)
