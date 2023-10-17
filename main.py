import random
import sys
import pygame

pygame.font.init()
pygame.mixer.init()
BINGO = pygame.mixer.Sound('resources/sound/bingo.mp3')
WOO = pygame.mixer.Sound('resources/sound/woo.mp3')
FONT30 = pygame.font.Font('resources/font/brlnsr.ttf', 30)
FONT35 = pygame.font.Font('resources/font/brlnsr.ttf', 35)
FONT40 = pygame.font.Font('resources/font/汉仪永字值日生简体.ttf', 40)


class Word:
    def __init__(self, word, answer, reference):
        self.image = FONT30.render(str(word), True, (255, 255, 255))
        self.rect = self.image.get_rect()
        self.word = word
        self.reference = reference
        self.answer = answer
        self.set_location()

    def set_location(self):
        self.rect.center = self.reference.rect.center
        self.rect = self.rect.move([0, 60])

    def update(self, screen):
        screen.blit(self.image, self.rect)


class Score:
    def __init__(self):
        self.score = 0
        self.image = FONT35.render(f'Score: {self.score}', True, (255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.center = 272, 50

    def reset_score(self, num):
        self.score += num
        self.image = FONT35.render(f'Score: {self.score}', True, (255, 255, 255))
        self.rect = self.image.get_rect()
        self.rect.center = 272, 50

    def update(self, screen):
        screen.blit(self.image, self.rect)


class Answer:
    def __init__(self, text):
        self.text = text
        self.image = FONT40.render(str(text), True, (0, 0, 0))
        self.rect = self.image.get_rect()
        self.set_location()

    def set_location(self):
        self.rect.center = 544 / 2, 820

    def update(self, screen):
        screen.blit(self.image, self.rect)


class Mole:
    FPS = 20

    def __init__(self, x, y):
        self.images = self.image_split()
        self.num = 0
        self.max = self.FPS * 5
        self.rect = self.image.get_rect()
        self.rect.center = x * 200 + 170, y * 200 + 190
        self.word = None

    @staticmethod
    def image_split():
        images = []
        image = pygame.image.load('resources/image/mole.png')
        width, height = image.get_rect().size
        width /= 5
        for index in range(5):
            new_image = image.subsurface((index * width, 0, width, height))
            images.append(pygame.transform.scale(new_image, (width, height)))
        return images

    @property
    def nums(self) -> int:
        if self.num + 1 < self.max:
            self.num = self.num + 1
        return self.num // self.FPS

    def guess(self, answer):
        if answer == self.word.answer:
            BINGO.play()
            return True
        WOO.play()
        return False

    def set_word(self, text, answer):
        self.word = Word(text, answer, self)

    @property
    def image(self):
        return self.images[self.nums]

    def update(self, screen):
        screen.blit(self.image, self.rect)
        self.word.update(screen)


class Scene:
    def __init__(self):
        self.image = pygame.image.load('resources/image/background.jpg')
        self.rect = self.image.get_rect()
        self.moles = self.init_moles()
        self.answer = None
        self.score = Score()
        self.data = self.loads_data()

    @staticmethod
    def loads_data():
        data = {}  # 读取文本里的单词 和 中文意思
        with open('resources/data/words.txt', encoding='utf-8') as f:
            words = f.readlines()
            for i in words:
                i = i.strip()
                answer, word, *_ = i.split(' ')  # 空格切分单词和中文意思
                data[word] = answer
        return data

    def reset_answer(self, text):
        answer = Answer(text)  # 实例化中文意思文字
        self.answer = answer

    def reset_words(self, words):
        for i in range(6):
            self.moles[i].num = 0  # 地鼠从土里钻出来的效果 使用num数值实现
            self.moles[i].set_word(words[i], self.data[words[i]])  # 设置地鼠的单词 以及单词的中文意思

    def reset(self):
        # words = random.simple(self.data.keys(), k=6) # 随机取出6个不同的单词
        # python3.9+ 已经弃用 random.simple 所以手写循环 替代
        l = list(self.data.keys())
        words = []
        while len(words) < 6:
            words.append(random.choice(l))
            l.remove(words[-1])

        answer = self.data[words[random.randint(0, 5)]]  # 随机选择一个单词 并拿到单词的中文意思
        self.reset_words(words)  # 重新绘制单词
        self.reset_answer(answer)  # 重新绘制底部中文意思

    # 我
    @staticmethod
    def init_moles():  # 生成6个地鼠类 并安置x,y位置(实际上x,y 是相对坐标 实例化Moles 会以x,y做加上比例再加上偏移量做出实际的 位置)
        moles = []
        for x in range(2):
            for y in range(3):
                moles.append(Mole(x, y))
        return moles

    def click(self, x, y):
        for mole in self.moles:  # 遍历地鼠列表 判断哪个地鼠被点击到
            if mole.rect.left < x < mole.rect.right and mole.rect.top < y < mole.rect.bottom:
                result = mole.guess(self.answer.text)  # 触发点击事件 计算匹配 单词和中文意思是否相同
                if result:  # 单词和中文意思匹配
                    self.score.reset_score(1)  # 得分 重新绘制分数
                    self.reset()  # 重新绘制单词意思 和中文提示词
                else:
                    mole.num = 0  # 让被点击的地鼠重新从土里钻出来(重置数值即可实现)

    def update(self, screen):
        screen.blit(self.image, self.rect)
        self.answer.update(screen) if self.answer else self.reset()
        for mole in self.moles:
            mole.update(screen)
        self.score.update(screen)


class Hammer:
    IMAGES = {
        0: pygame.image.load('resources/image/hammer00.png'),
        1: pygame.image.load('resources/image/hammer01.png')
    }

    def __init__(self):
        self.num = 0
        self.image = self.IMAGES[self.num]
        self.rect = self.image.get_rect()

    def click(self):
        if self.num == 0:
            self.num = 1
        else:
            self.num = 0
        self.image = self.IMAGES[self.num]

    def update(self, screen):
        self.rect.center = pygame.mouse.get_pos()
        screen.blit(self.image, self.rect)


class Game:
    # 可做场景切换的游戏架构类
    def __init__(self):
        self.running = True
        self.screen = pygame.display.set_mode([544, 900])
        self.scene = Scene()
        self.cursor = Hammer()
        self.clock = pygame.time.Clock()
        self.moles = []

    def update(self):
        self.scene.update(self.screen)
        self.cursor.update(self.screen)
        pygame.display.update()

    def start(self):
        while self.running:
            self.clock.tick(150)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    self.cursor.click()
                elif event.type == pygame.MOUSEBUTTONUP:
                    position = event.pos
                    self.cursor.click()
                    self.scene.click(*position)

            self.update()
        pygame.quit()
        sys.exit()


if __name__ == '__main__':
    g = Game()
    g.start()
