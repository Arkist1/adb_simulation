            if bl.pos[0] >= globals.SCREEN_WIDTH:
                bullets.remove(bl)
            elif bl.pos[0] < 0:
                bullets.remove(bl)
            elif bl.pos[1] >= globals.SCREEN_HEIGHT:
                bullets.remove(bl)
            elif bl.pos[1] < 0:
                bullets.remove(bl)