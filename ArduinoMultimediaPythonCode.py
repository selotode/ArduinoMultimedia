# Изработиле:
# Иван Марковски 185051
# Кристијан Николиќ 185006
import serial, time, pafy, vlc
import pywhatkit as p

# Конекција со ардуино на порта COM3 и брзина на сигнали 9600
serPort = "COM3"
baudRate = 9600
ser = serial.Serial(serPort, baudRate, timeout=5)
print("Отворено на порта " + serPort + " со брзина  Baudrate " + str(baudRate))
time.sleep(2)

# знаменце за дали е паузирана песна или не
paused = False

# низа од песни
songNames = []
# дали е пуштена некоја песна
playing = 0
# индекс на тековно пуштени песни
current_index = 0
# индекс на претпоследниот елемент во низата
array_index = 0

# креирање на VLC инстанца
Instance = vlc.Instance()
player = Instance.media_player_new()

# дали е пуштено на bluetooth(1) или на мемориска(0)
bluetooth = 1


# Функција за читање од ардуино
def readArduino():
    data = ser.readline()
    return data

# Функција за парсирање на пораката, односно тргање на знаменца и големи букви
def parseData(data):
    msg = data.decode().lower()
    msg = msg.strip()
    return msg

# Функција за пуштање на песната
def playSong(songName):
  #Доколку не е празно име
    if songName is None:
      return
    # Функција која пребарува на youtube и враќа линк до песна
    url = p.playonyt(songName)

    # креирање на видео објект од линкот
    video = pafy.new(url)

    # зимање на најдобрата слика
    best = video.getbest()

    # преземање на податоците на најдобрата слика
    playurl = best.url

    # креирање на објект медиа од VLC со видеото и неговото аудио
    Media = Instance.media_new(playurl)
    Media.get_mrl()

    # спремање на пуштање на видеото
    player.set_media(Media)

    # пуштање на видеото
    player.play()

    # порака за кое видео е пуштено ( пораката се исчитува во пајтон конзола )
    playingMsg = "Моментално е пуштена " + video.title + "...."
    print(playingMsg)


while True:

    # проверка дали е тековно пуштена некоја песна
    playing = player.is_playing()

    # повикување на функција за читање од ардуино
    data = readArduino()
    # парсирање на пораката
    msg = parseData(data)
    if msg:
      #разделување на пораката во низа, каде на 0 позиција се наоѓа командата
        splitMessage = msg.split()

        # случај ако е bluetooth вклучен
        if bluetooth:

            # пуштање на пораката доколку е напишано play, додавање во низа, и зголемување на иденксот на низата
            if splitMessage[0] in ("play", "p"):
                songNames.insert(array_index, splitMessage[1:])
                array_index += 1
                songNames.insert(array_index, None)
            # доколку е напишано за упатство да се врати упатството
            elif splitMessage[0] in ("man", "m", "manual", "help", "h"):   
                ser.write(bytes("0", 'utf-8'))
            # проверка за паузирање на песната
            elif splitMessage[0] in "pause" and not paused and playing:
                player.pause()
                paused = True
            # проверка за продолжување на песната
            elif splitMessage[0] in ("r", "resume") and paused:
                player.pause()
                paused = False
            # проверка за стоп на песната
            elif splitMessage[0] in "stop":
                player.stop()
                songNames = []
                current_index = 0
                array_index = 0
            # проверка за промена на мемориска, се прекинува музиката и се враќаат сите променливи на почетни
            elif splitMessage[0] in ("s","sd"):
                bluetooth = 0
                player.stop()
                songNames = []
                current_index = 0
                array_index = 0
                ser.write(bytes("s",'utf-8'))

            # проверка за следна песна, се проверува дали има воопшто песна во низата ако има
            # се стопира тековната и се пушта следната, доколку нема се печати нема песна
            elif splitMessage[0] in ("n", "next"):
                if len(songNames) and songNames[current_index] is not None:
                    player.stop()
                    playSong(songNames[current_index])
                    current_index += 1
                    time.sleep(5)
                else:
                    ser.write(bytes("1",'utf-8'))
        # else за команди за мемориска
        else:
            # проверка за упатство
            if splitMessage[0] in ("man", "m", "manual", "help", "h"):
                ser.write(bytes("0", 'utf-8'))
            # проверка за пуштање на песна
            elif splitMessage[0] in ("play", "p"):
                ser.write(bytes("1", 'utf-8'))
            # проверка за стоп
            elif splitMessage[0] in "stop":
                ser.write(bytes("2", 'utf-8'))
            # проверка за следна песна
            elif splitMessage[0] in ("n", "next"):
                ser.write(bytes("3", 'utf-8'))
            # проверка за назад
            elif splitMessage[0] in ("b", "back"):
                ser.write(bytes("4", 'utf-8'))
            # проверка за паузирање
            elif splitMessage[0] in "pause":
                ser.write(bytes("5", 'utf-8'))
            # проверка за продолжување
            elif splitMessage[0] in "resume":
                ser.write(bytes("5", 'utf-8'))
            # проверка за промена од мемориска на bluetooth
            elif splitMessage[0] in ("bt", "bluetooth"):
                ser.write(bytes("b",'utf-8'))
                bluetooth = 1

    #доколку заврши песната автоматски да се промени на следната
    if not playing and len(songNames) and bluetooth:
        playSong(songNames[current_index])
        current_index += 1
        time.sleep(5)
