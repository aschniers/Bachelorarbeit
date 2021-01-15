import unreal

def spawn():
    global actors
    actors = []
    z = 0 
    y = 2500
    turn = 0
    landscapesize = 25195 - 350
    actor_class_wheat = unreal.EditorAssetLibrary.load_blueprint_class('/Game/Plants')
    actor_class_oat = unreal.EditorAssetLibrary.load_blueprint_class('/Game/Oat/oat')
    datei = open('C:/Users/annas/Documents/Python Scripts/positions.txt','w+')

    #airsim has a different scale, so the positions need to be divided by 100
    datei.write(str(float(y)/100) + " " + str(float(z)/100) +"\n")
    for x in range(-landscapesize, landscapesize + 350, 700):
        datei.write(str((float(x)/100)-1.55) + "\n")
        for i in range(2):
            #place a row of wheat and a row of oats
            if i == 0:
                actor_class = actor_class_wheat
                y = -y
            else:
                actor_class = actor_class_oat
                y= -y
            actor_location = unreal.Vector(x, y, z)            
            actor_rotation = unreal.Rotator(0.0, 0.0, turn)
            actors.append(unreal.EditorLevelLibrary.spawn_actor_from_class(actor_class, actor_location, actor_rotation))
            turn += 2.5
def remove():
    for actor in actors:
        unreal.EditorLevelLibrary.destroy_actor(actor)
