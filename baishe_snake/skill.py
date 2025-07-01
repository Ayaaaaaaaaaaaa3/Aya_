class SkillTree:
    def __init__(self):
        self.exp = 0
        self.skills = {
            "invincible": False,
            "fly": False,
            "shockwave": False,
            "pause": False
        }
        self.invincible_timer = 0  # 无敌剩余帧数

    def gain_exp(self, amount):
        self.exp += amount
        # 简单示例：经验达到一定值自动解锁技能
        if self.exp >= 10:
            self.skills["fly"] = True
        if self.exp >= 20:
            self.skills["shockwave"] = True
        if self.exp >= 30:
            self.skills["pause"] = True

    def use_skill(self, skill_name, duration=100):
        if skill_name == "invincible":
            self.skills["invincible"] = True
            self.invincible_timer = duration  # 例如100帧
        elif self.skills.get(skill_name, False):
            # 触发其它技能效果
            return True
        return False

    def update(self):
        if self.skills["invincible"]:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.skills["invincible"] = False
                self.invincible_timer = 0

    def is_invincible(self):
        return self.skills["invincible"]
