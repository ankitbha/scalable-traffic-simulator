
# car length (meters)
CAR_LENGTH = 5

# time spacing can be 0.6, 0.9, 2 or 3, depending on what we choose. I
# suggest 0.9 seconds, using the arguments in the traffic jams paper.
TIME_SPACING = 0.9

# car_spacing = (1 / density) - 1
# c = 1/x - 1
def get_car_spacing(speed, time_spacing):
    # assuming speed is in kmph, and time_spacing is in seconds,
    # output will be in meters
    car_spacing = (speed * time_spacing * 5) / (CAR_LENGTH * 18)
    return car_spacing

def get_max_possible_speed(car_spacing, time_spacing):
    # assuming car_spacing is in meters, time_spacing is in seconds,
    # output will be in kmph
    return (car_spacing * CAR_LENGTH) * 18 / (time_spacing * 5)

# density = 1 / (1 + car_spacing)
# x = 1/(1+c) 
def get_density(speed, time_spacing):
    # assuming speed is in kmph and time_spacing is in seconds
    return 1 / (1 + get_car_spacing(speed, time_spacing))

def get_exitrate(speed, time_spacing = TIME_SPACING):
    # exit rate is number of cars exiting per second
    car_spacing = get_car_spacing(speed, time_spacing)
    exitrate = speed / (CAR_LENGTH + car_spacing)
    return exitrate


# print(get_exitrate( 50, TIME_SPACING))
