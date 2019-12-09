

def play_sound(input, streamer='pygame'):
    print('Playing sound {}'.format(input))
    #
    if streamer == 'pygame':
        from pygame import mixer
        mixer.pre_init(44100, -16, 1, 512)
        mixer.init()
        mixer.music.load(input)
        mixer.music.play()
        while mixer.music.get_busy() == True:
            continue
    elif streamer == 'playsound': 
        from playsound import playsound
        playsound(input)
    elif streamer == 'os':
        import subprocess
        subprocess.call(['omxplayer', input])
    else:
        raise NotImplementedError