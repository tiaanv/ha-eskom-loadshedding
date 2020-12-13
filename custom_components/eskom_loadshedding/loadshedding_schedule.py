import const
import datetime
import logging

def getAreaCodesByTimeSlot(stage, day, timeSlot):
    day = _clipDayToGroup(day)
    areaCodeAcc = _getAreaCodeAccumulationDayStart(stage, day) + timeSlot
    areaCode = _nomalizeAreaCode(stage, areaCodeAcc)
    areaCodes = [areaCode]

    if (stage == 4 and timeSlot == 4 and day == 15):
        areaCodes = []

    if (stage > 1):
        areaCodes = areaCodes + getAreaCodesByTimeSlot(stage - 1, day, timeSlot)

    return areaCodes

def getAreaCodesByTimeValue(stage, day, time, includeoverlap = False, previousMonthLastDay = 31):
    isOddHour = time.hour % const.TIME_SLOT_HOURS != 0
    timeSlot = _getTimeslotFromHour(time.hour)

    areaCodes = getAreaCodesByTimeSlot(stage, day, timeSlot)

    if (includeoverlap and (not isOddHour) and time.minute <= const.TIME_SLOT_MINUTES):
        if (timeSlot > 1):
            timeSlot -= 1
        else:
            timeSlot = const.NUM_TIME_SLOTS

            if (day > 1):
                day -= 1
            else:
                day = previousMonthLastDay
        
        areaCodes = areaCodes + getAreaCodesByTimeSlot(stage, day, timeSlot)

    return areaCodes

def getTimeSlotsByAreaCode(stage, day, areaCode):
    timeSlots = []
    for i in range(const.NUM_TIME_SLOTS):
        areas = getAreaCodesByTimeSlot(stage, day, i + 1)
        try:
            if (areas.index(areaCode) > -1):
                timeSlots.append(i + 1)
                continue
        except:
            pass

    return timeSlots

def getNextTimeSlotInDay(stage, day, areaCode, fromHour = -1):
    slots = getTimeSlotsByAreaCode(stage, day, areaCode)

    for slot in slots:
        slotHour = getTimeSlotHour(slot)

        if (fromHour == -1 or slotHour > fromHour):
            return slot

    return 0

def getNextTimeSlot(stage, areaCode):
    result = {
        "slot": None,
        "day": None,
        "date": None
    }

    if (stage < 1 or stage > const.HIGHEST_STAGE):
        logging.warning("getNextTimeSlot() stage out of bounds")
        return result

    if (areaCode < 1 or areaCode > const.NUM_AREA_CODES):
        logging.warning("getNextTimeSlot() areaCode out of bounds")
        return result

    d = datetime.datetime.now()
    fromHour = d.hour
    fromDay = d.day

    slot = None
    day = fromDay
    dayAccum = 0

    while (slot == None):
        slot = getNextTimeSlotInDay(stage, day, areaCode, fromHour if day == fromDay else -1)

        if (slot == None):
            if (day >= const.MAX_MONTH_DAY):
                day = 1
            else:
                day += 1

            dayAccum += 1

    newDate = datetime.datetime(d.year,d.month,d.day,getTimeSlotHour(slot),0,0)
    newDate = newDate + datetime.timedelta(days=dayAccum)

    result["slot"] = slot
    result["day"] = day
    result["date"] = newDate

    return result


def isLoadSheddingNow(stage, areaCode):
    d = datetime.datetime.now()
    hour = d.hour
    areaCodes = getAreaCodesByTimeValue(stage, d.day, d.hour, d.minute)

    result = {
        "status": False,
        "endDate": None
    }

    try:
        if (areaCodes.index(areaCode) > -1):
            result["status"] = True
    except:
        pass

    if (result["status"]):
        slot = _getTimeslotFromHour(hour)
        endDate = datetime.datetime(d.year,d.month,d.day,getTimeSlotHour(slot) + const.TIME_SLOT_HOURS,const.TIME_SLOT_MINUTES)
        result["endDate"] = endDate

    return result


def getTimeSlotHour(slot):
    return (slot - 1) * const.TIME_SLOT_HOURS

def _getTimeslotFromHour(hour):
    isOddHour = (hour % const.TIME_SLOT_HOURS) != 0

    timeSlot = hour
    if isOddHour:
       timeSlot -= 1

    return timeSlot // const.TIME_SLOT_HOURS + 1

def _clipDayToGroup(day):
    if (day > const.NUM_DAY_GROUPS):
        day -= const.NUM_DAY_GROUPS
    return day

def _getAreaCodeAccumulationDayStart(stage, day):
    if (day <= 1):
        return 0
    
    dayBefore = day - 1
    areaCodeAcc = dayBefore * const.NUM_TIME_SLOTS

    for i in const.DAY_AREA_EXTRA_INCREMENTS:
        if (day >= i):
            areaCodeAcc += 1
        

    if (stage <= 4):
        for i in const.DAY_AREA_EXTR_INCREMENTS_STAGE_LOWER:
            if (day >= i):
                areaCodeAcc += 1
    
    return areaCodeAcc

def _nomalizeAreaCode(stage, areaCodeAcc):
    areaCode = areaCodeAcc % const.NUM_AREA_CODES
    areaCode += const.STAGE_STARTING_AREAS[stage] - 1
    if (areaCode > const.NUM_AREA_CODES):
        areaCode -= const.NUM_AREA_CODES

    return areaCode


nextday = getNextTimeSlot(2, 6)["day"]
nextslot = getNextTimeSlot(2, 6)["slot"]
print(nextslot)
print(nextday)
print(getTimeSlotHour(nextslot))
print(getNextTimeSlot(2, 6)["date"])
print(getAreaCodesByTimeSlot(2, 15, 3))
print(getAreaCodesByTimeValue(2, 7, datetime.time(hour=1,minute=52)))
print(getAreaCodesByTimeValue(3, 26, datetime.time(hour=14, minute=25), True))
print(getTimeSlotsByAreaCode(4, 3, 11))