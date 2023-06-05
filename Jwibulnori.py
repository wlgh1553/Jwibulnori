from vpython import*
import random as rand

#버튼
def startbtn(b):
    b.disabled=True
    return b.disabled
#스타트 버튼
btnStart = button(text = "Shoot", bind=startbtn)

#상수 초기화
g = vec(0,-9.8,0)
Cd = 0.35 #공의 저항계수
rho = 1.3 #공기 밀도
e = 1 #반발계수 (탄성충돌)

#조정값
default_m = 1
default_R = 1.5
default_velo = 8
default_pos = -4

#ground생성
ground = box(pos = vec(0,-4,0), size = vec(20,-0.01,5))

#monster
monsterCnt=30
#monster 위치벡터 리스트, 초기화
monsterPosList = list()
for i in range(monsterCnt):
    monsterPosList.append(vec(rand.uniform(10, 13),-4,0))
#monster 입자 리스트, 초기화
monsterList=list()
for r in (monsterPosList):
    acc = rand.uniform(0.01, 0.2)
    velo = rand.uniform(0.1,0.7)
    monsterList.append(cylinder(pos=r,color=color.white,a=vec(-acc,0,0), 
                        v=vec(-velo,0,0), radius=0.2,axis=vec(0,1,0), 
                        is_coll = False, m=default_m*10))

#객체 생성
bullet = sphere(pos=vec(default_pos,-default_R,0), v = vec(-default_velo,0,0),
            m=default_m, color=color.red, radius=0.1,make_trail = True)
pointer = arrow(pos=vec(default_pos,0,0), axis = vec(0,-default_R,0), shaftwidth=0.03)
btnStart.disabled = False
t=0
dt=0.01
is_circle = True

is_collision = False
cnt_alive_monster = monsterCnt
for r in (monsterList):
    r.visible = False

#게임 메인 루프
while True:
    rate(1/dt)

    #공 업데이트
    #원운동
    if is_circle:
        if btnStart.disabled==True:
            is_circle=False
        else:
            #원운동 실행
            acc = mag(bullet.v)**2 / default_R
            bullet.a = cross(norm(bullet.v), vec(0,0,1)) * acc
            bullet.v = bullet.v + bullet.a * dt
            bullet.pos = bullet.pos + bullet.v * dt
            pointer.axis = vec(bullet.pos.x - default_pos, bullet.pos.y, 0)
            
            #속도 너무 빨라지면 다시 처음으로 돌아오기
            if mag(bullet.v)>default_velo+1 and abs(bullet.pos.x - default_pos)<0.1 and bullet.pos.y < -1.4:
                bullet.pos = vec(default_pos,-default_R,0)
                bullet.v = vec(-default_velo,0,0)
            
    #포물선운동
    else:
        Fg = g*bullet.m
        drag = -0.5*rho*Cd*(pi*bullet.radius**2)*mag(bullet.v)**2*norm(bullet.v)
        bullet.a = (Fg + drag)/bullet.m
        bullet.v = bullet.v + bullet.a*dt
        bullet.pos = bullet.pos + bullet.v*dt
        bullet.pos.z=0

        #바닥에 떨어지면 없애기
        if bullet.pos.y - bullet.radius <= ground.pos.y or bullet.pos.x > 10 or bullet.pos.x < -10:
            #흔적 지우기
            bullet.make_trail = False
            bullet.visible = False
            bullet.clear_trail()

            #원운동 초기 설정
            bullet.pos=vec(default_pos,-default_R,0)
            bullet.v = vec(-default_velo,0,0)
            pointer.axis = vec(0,-default_R,0)
            bullet.make_trail = True
            bullet.visible = True

            #다시 원운동으로 돌아감
            is_circle=True
            btnStart.disabled=False
            is_collision = False

    #몬스터 업데이트
    for r in (monsterList):
        #나타나기
        if r.visible==False and r.pos.x<10 and r.is_coll==False:
            r.visible=True
        #이동
        if r.pos.x > -10:
            r.v = r.v + r.a*dt
            r.pos = r.pos + r.v*dt
        #충돌
        if mag(r.pos - bullet.pos) < r.axis.y + bullet.radius and r.visible == True:
            bullet_v_f = ((bullet.m-e*r.m)*bullet.v + (1+e)*r.m*r.v) / (bullet.m + r.m)
            r_v_f = ((r.m-e*bullet.m)*r.v + (1+e)*bullet.m*bullet.v) / (bullet.m + r.m)
            bullet.v = bullet.v + bullet_v_f
            is_collision = True
            r.is_coll = True
            r.visible = False
            print("collision!!", mag(bullet.v))
            cnt_alive_monster-=1
    
    #종료조건 : 움직이는 몬스터가 없는 경우
    finish_cnt = 0
    for r in (monsterList):
        if r.pos.x <= -10 and r.visible:
            finish_cnt+=1
    
    #종료
    if finish_cnt == cnt_alive_monster or cnt_alive_monster==0:
        str = "defence : " +"{}".format(monsterCnt-cnt_alive_monster) + "/" + "{}".format(monsterCnt)
        L=label(pos=vec(0,0,0), text=str, color=color.red,
                border=3, font='sans', box=False)
        break
    t+=dt