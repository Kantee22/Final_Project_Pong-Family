import os
import ball
import my_event
import turtle
import heapq
import paddle
import time


class BouncingSimulator:
    def __init__(self,
                 num_ba: int = 1,
                 p1: str = 'P1',
                 p2: str = 'P2'):
        self.num_balls = num_ba
        self.p1 = p1
        self.p2 = p2
        self.ball_list = []
        self.t = 0.0
        self.pq = []
        self.hz = 4
        turtle.speed(0)
        turtle.tracer(0)
        turtle.hideturtle()
        turtle.colormode(255)
        self.canvas_width = turtle.screensize()[0]
        self.canvas_height = turtle.screensize()[1]

        ball_radius = 0.05 * self.canvas_width
        self.ball = ball.Ball(ball_radius, 0, 0, -3, 4, (255, 0, 255), 0)
        self.ball_list.append(self.ball)

        tom = turtle.Turtle()
        self.my_paddle = paddle.Paddle(300, 15, (255, 0, 0), tom)
        self.my_paddle.set_location([0, -250])
        self.my_paddle2 = paddle.Paddle(300, 15, (255, 0, 0), tom)
        self.my_paddle2.set_location([0, 250])

        self.screen = turtle.Screen()
        self.score1 = 0
        self.score2 = 0
        self.score_display = turtle.Turtle()
        self.score_display.hideturtle()
        self.score_display.penup()
        self.score_display.goto(0, 260)
        self.display_score()

    def check_goal(self):
        if self.ball.y - self.ball.size == -self.canvas_height:
            self.ball.vx *= -1
            self.score1 += 1
            self.check_win()
            self.reset_paddle()
            self.stop_game_for_score()
            self.reset_ball()
        elif self.ball.y + self.ball.size == self.canvas_height:
            self.ball.vx *= -1
            self.score2 += 1
            self.check_win()
            self.reset_paddle()
            self.stop_game_for_score()
            self.reset_ball()

    def display_score(self):
        self.score_display.clear()
        self.score_display.write(f"{self.p1}: {self.score1}  {self.p2}: {self.score2}",
                                 align="center", font=("Courier", 24, "normal"))

    def check_win(self):
        if self.score1 >= 3:
            self.screen.clear()
            self.ball.vx = 0
            self.ball.vy = 0.0001
            self.end_game(self.p1)
        elif self.score2 >= 3:
            self.screen.clear()
            self.ball.vx = 0
            self.ball.vy = 0.0001
            self.end_game(self.p2)

    def end_game(self, winner):
        turtle.clear()
        turtle.hideturtle()
        self.screen.bgpic("score.gif")
        self.score_display.goto(0, 0)
        self.score_display.color("black")
        self.score_display.write("GAME OVER", align="center", font=("Courier", 36, "normal"))
        self.score_display.goto(0, -50)
        self.score_display.write(f"{winner} WINS!", align="center", font=("Courier", 24, "normal"))

    def fix(self):
        if (self.ball.y + self.ball.size > 240 and self.ball.y + self.ball.size < 250) and \
                (self.my_paddle2.location[0] + 135 > self.ball.x +
                 self.ball.size > self.my_paddle2.location[0] - 135):
            self.my_paddle2.width *= 0.9
        if (self.ball.y - self.ball.size < -240 and self.ball.y - self.ball.size > -250) and \
                (self.my_paddle.location[0] + 135 > self.ball.x -
                 self.ball.size > self.my_paddle.location[0] - 135):
            self.my_paddle.width *= 0.9

    def stop_game_for_score(self):
        time.sleep(1.5)
        self.display_score()

    def reset_ball(self):
        self.ball.x = 0
        self.ball.y = 0

    def reset_paddle(self):
        self.my_paddle.width = 300
        self.my_paddle.set_location([0, -250])
        self.my_paddle2.width = 300
        self.my_paddle2.set_location([0, 250])

    def __predict(self, a_ball):
        if a_ball is None:
            return

        dtx = a_ball.time_to_hit_vertical_wall()
        dty = a_ball.time_to_hit_horizontal_wall()
        heapq.heappush(self.pq, my_event.Event(self.t + dtx, a_ball, None, None))
        heapq.heappush(self.pq, my_event.Event(self.t + dty, None, a_ball, None))

    def __draw_border(self):
        turtle.penup()
        turtle.goto(-self.canvas_width, -self.canvas_height)
        turtle.pensize(5)
        turtle.pendown()
        turtle.color((0, 0, 0))
        for _ in range(2):
            turtle.color((255, 255, 255))
            turtle.forward(2*self.canvas_width)
            turtle.left(90)
            turtle.color((0, 0, 0))
            turtle.forward(2*self.canvas_height)
            turtle.left(90)
        if self.score1 >= 3 or self.score2 >= 3:
            turtle.hideturtle()

    def __redraw(self):
        turtle.clear()
        self.my_paddle.clear()
        self.my_paddle2.clear()
        self.__draw_border()
        self.my_paddle.draw()
        self.my_paddle2.draw()
        self.ball.draw()
        turtle.update()
        heapq.heappush(self.pq, my_event.Event(self.t + 1.0/self.hz, None, None, None))

    def __paddle_predict(self):
        a_ball = self.ball_list[0]
        dtp1 = a_ball.time_to_hit_paddle(self.my_paddle)
        heapq.heappush(self.pq, my_event.Event(self.t + dtp1, a_ball, None, self.my_paddle))

    def __paddle_predict2(self):
        a_ball = self.ball_list[0]
        dtp2 = a_ball.time_to_hit_paddle(self.my_paddle2)
        heapq.heappush(self.pq, my_event.Event(self.t + dtp2, a_ball, None, self.my_paddle2))

    def move_left(self):
        if (self.my_paddle.location[0] - self.my_paddle.width/2 - 40) >= -self.canvas_width:
            self.my_paddle.set_location([self.my_paddle.location[0] - 40,
                                         self.my_paddle.location[1]])

    def move_left2(self):
        if (self.my_paddle2.location[0] - self.my_paddle2.width/2 - 40) >= -self.canvas_width:
            self.my_paddle2.set_location([self.my_paddle2.location[0] - 40,
                                          self.my_paddle2.location[1]])

    def move_right(self):
        if (self.my_paddle.location[0] + self.my_paddle.width/2 + 40) <= self.canvas_width:
            self.my_paddle.set_location([self.my_paddle.location[0] + 40,
                                         self.my_paddle.location[1]])

    def move_right2(self):
        if (self.my_paddle2.location[0] + self.my_paddle2.width/2 + 40) <= self.canvas_width:
            self.my_paddle2.set_location([self.my_paddle2.location[0] + 40,
                                          self.my_paddle2.location[1]])

    def run(self):
        self.__predict(self.ball)
        heapq.heappush(self.pq, my_event.Event(0, None, None, None))

        # listen to keyboard events and activate move_left and move_right handlers accordingly
        self.screen.listen()
        self.screen.onkeypress(self.move_left, "Left")
        self.screen.onkeypress(self.move_right, "Right")
        self.screen.onkeypress(self.move_left2, "a")
        self.screen.onkeypress(self.move_right2, "d")

        while True:
            e = heapq.heappop(self.pq)
            if not e.is_valid():
                continue

            ball_a = e.a
            ball_b = e.b
            paddle_a = e.paddle

            # update positions, and then simulation clock
            self.ball.move(e.time - self.t)
            self.t = e.time
            self.check_goal()
            self.fix()

            if (ball_a is not None) and (ball_b is not None) and (paddle_a is None):
                ball_a.bounce_off(ball_b)
            elif (ball_a is not None) and (ball_b is None) and (paddle_a is None):
                ball_a.bounce_off_vertical_wall()
            elif (ball_a is None) and (ball_b is not None) and (paddle_a is None):
                ball_b.bounce_off_horizontal_wall()
            elif (ball_a is None) and (ball_b is None) and (paddle_a is None):
                self.__redraw()
            elif (ball_a is not None) and (ball_b is None) and (paddle_a is not None):
                ball_a.bounce_off_paddle()

            self.__predict(ball_a)
            self.__predict(ball_b)

            # regularly update the prediction for the paddle as its
            # position may always be changing due to keyboard events
            self.__paddle_predict()
            self.__paddle_predict2()

        # hold the window; close it by clicking the window close 'x' mark
        turtle.done()

# Set up screen


screen = turtle.Screen()
screen.bgcolor("black")
screen.bgpic("Screen 1.gif")
audio_file = "Background"
os.system(f"start wmplayer {audio_file}")
num_balls = 1
P1 = str(input("P1 NAME "))
P2 = str(input("P2 NAME "))
turtle.delay(1000)
my_simulator = BouncingSimulator(num_balls, P1, P2)
my_simulator.run()
