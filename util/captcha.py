import Image, ImageDraw, ImageFont
from random import randint, choice, seed
import time

fname = '/usr/share/dict/words'
words = """account,act,addition,adjustment,advertisement,agreement,air,amount,amusement,animal,answer,apparatus,approval,argument,art,attack,attempt,attention,attraction,authority,back,balance,base,behavior,belief,birth,bit,bite,blood,blow,body,brass,bread,breath,brother,building,burn,burst,business,butter,canvas,care,cause,chalk,chance,change,cloth,coal,color,comfort,committee,company,comparison,competition,condition,connection,control,cook,copper,copy,cork,cotton,cough,country,cover,crack,credit,crime,crush,cry,current,curve,damage,danger,daughter,day,death,debt,decision,degree,design,desire,destruction,detail,development,digestion,direction,discovery,discussion,disease,disgust,distance,distribution,division,doubt,drink,driving,dust,earth,edge,education,effect,end,error,event,example,exchange,existence,expansion,experience,expert,fact,fall,family,father,fear,feeling,fiction,field,fight,fire,flame,flight,flower,fold,food,force,form,friend,front,fruit,glass,gold,government,grain,grass,grip,group,growth,guide,harbor,harmony,hate,hearing,heat,help,history,hole,hope,hour,humor,ice,idea,impulse,increase,industry,ink,insect,instrument,insurance,interest,invention,iron,jelly,join,journey,judge,jump,kick,kiss,knowledge,land,language,laugh,law,lead,learning,leather,letter,level,lift,light,limit,linen,liquid,list,look,loss,love,machine,man,manager,mark,market,mass,meal,measure,meat,meeting,memory,metal,middle,milk,mind,mine,minute,mist,money,month,morning,mother,motion,mountain,move,music,name,nation,need,news,night,noise,note,number,observation,offer,oil,operation,opinion,order,organization,ornament,owner,page,pain,paint,paper,part,paste,payment,peace,person,place,plant,play,pleasure,point,poison,polish,porter,position,powder,power,price,print,process,produce,profit,property,prose,protest,pull,punishment,purpose,push,quality,question,rain,range,rate,ray,reaction,reading,reason,record,regret,relation,religion,representative,request,respect,rest,reward,rhythm,rice,river,road,roll,room,rub,rule,run,salt,sand,scale,science,sea,seat,secretary,selection,self,sense,servant,sex,shade,shake,shame,shock,side,sign,silk,silver,sister,size,sky,sleep,slip,slope,smash,smell,smile,smoke,sneeze,snow,soap,society,son,song,sort,sound,soup,space,stage,start,statement,steam,steel,step,stitch,stone,stop,story,stretch,structure,substance,sugar,suggestion,summer,support,surprise,swim,system,talk,taste,tax,teaching,tendency,test,theory,thing,thought,thunder,time,tin,top,touch,trade,transport,trick,trouble,turn,twist,unit,use,value,verse,vessel,view,voice,walk,war,wash,waste,water,wave,wax,way,weather,week,weight,wind,wine,winter,woman,wood,wool,word,work,wound,writing,year,angle,ant,apple,arch,arm,army,baby,bag,ball,band,basin,basket,bath,bed,bee,bell,berry,bird,blade,board,boat,bone,book,boot,bottle,box,boy,brain,brake,branch,brick,bridge,brush,bucket,bulb,button,cake,camera,card,cart,carriage,cat,chain,cheese,chest,chin,church,circle,clock,cloud,coat,collar,comb,cord,cow,cup,curtain,cushion,dog,door,drain,drawer,dress,drop,ear,egg,engine,eye,face,farm,feather,finger,fish,flag,floor,fly,foot,fork,fowl,frame,garden,girl,glove,goat,gun,hair,hammer,hand,hat,head,heart,hook,horn,horse,hospital,house,island,jewel,kettle,key,knee,knife,knot,leaf,leg,library,line,lip,lock,map,match,monkey,moon,mouth,muscle,nail,neck,needle,nerve,net,nose,nut,office,orange,oven,parcel,pen,pencil,picture,pig,pin,pipe,plane,plate,plough/plow,pocket,pot,potato,prison,pump,rail,rat,receipt,ring,rod,roof,root,sail,school,scissors,screw,seed,sheep,shelf,ship,shirt,shoe,skin,skirt,snake,sock,spade,sponge,spoon,spring,square,stamp,star,station,stem,stick,stocking,stomach,store,street,sun,table,tail,thread,throat,thumb,ticket,toe,tongue,tooth,town,train,tray,tree,trousers,umbrella,wall,watch,wheel,whip,whistle,window,wing,wire,worm"""
words = words.split(",")

CAPTCHA_WIDTH_ORIG = 100
CAPTCHA_HEIGHT_ORIG = 12
CAPTCHA_WIDTH = 300
CAPTCHA_HEIGHT = 36

def makekey():
    seed(time.time())
    key = ""
    for i in range(32):
        key += choice("abcdefghijklmnopqrstuvwxyz1234567890")
    return key
    
def makeword(key=time.time()):
    seed(key)
    w = choice(words).strip().lower()
    seed(time.time())
    return w
    
def makeimage(text):
    seed(text)
    img = Image.new("RGBA", (CAPTCHA_WIDTH_ORIG, CAPTCHA_HEIGHT_ORIG), (255, 0, 0))
    draw = ImageDraw.ImageDraw(img)
    for i in range(100):
        x = randint(-10,100)
        y = randint(-10,10)
        r = ((x, y), (x+randint(0,6),y+randint(0,10)))
        draw.rectangle(r, fill=choice(((0,0,0), (255, 255, 255))))
    total_length = draw.textsize(text)[0]
    x = CAPTCHA_WIDTH_ORIG-total_length-len(text)*4
    if x < 0:
        x = 0
    else:
        x = randint(0, x)
    for c in text:
        y = randint(-1,0)
        w, h = draw.textsize(c)
        r = (x, y), (x+w, y+h)
        g = choice( (randint(0,50), randint(200,255)) )
        draw.rectangle(r, fill=(255-g,255-g,255-g))
        draw.text((x, y), c, fill=(g,g,g))
        x += w + randint(0,4)
    seed(time.time())
    return img.resize((CAPTCHA_WIDTH, CAPTCHA_HEIGHT), resample=Image.BICUBIC)
    
if __name__=='__main__':
    w = makeword()
    print w
    makeimage(w).save("test.png")