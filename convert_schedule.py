import numpy as np
from PIL import Image
import pytesseract
import pytz
from icalendar import Calendar, Event
from datetime import datetime, time, timedelta
import dateutil
from dateutil.rrule import rrule, WEEKLY, MONTHLY, MO, TU, WE, TH, FR # For defining recurring rules
import re

def imgToArray(imgLocation):
    img = Image.open(imgLocation)  
    print(img.width, img.height)
    img = img.convert("L")
    return np.array(img)

def showImg(pixels):
    img = Image.fromarray(pixels,mode='L')
    img.show()

def time_to_TDelta(x):
  add = 0
  if (x[5] == 'P') and ((x[0]+x[1]) != '12'):
    add += 12
  if x[0] == '0':
    if x[3] == '0':
      return time(int(x[1])+add,int(x[4]))
    else:
      return time(int(x[1])+add,int(x[3]+x[4]))
  else:
    if x[3] == '0':
      return time(int(x[0]+x[1])+add,int(x[4]))
    else:
      return time(int(x[0]+x[1])+add,int(x[3]+x[4]))

pixelsOrg = imgToArray("/content/Schedule1.png")
    img = Image.open("/content/Schedule1.png")
    #binarized the array
    th = 128
    pixels = np.copy(pixelsOrg)
    for i in range(len(pixels)):
        for j in range(pixels.shape[1]):
            if pixels[i][j] < th:
                pixels[i][j] = 0
            else:
                pixels[i][j] = 255
    count = 0
    line_h = []
    for i in range(len(pixels)):
        count = 0
        for j in range(pixels.shape[1]):
            if pixels[i][j] == 0:
                count+= 1
            if count>img.width-100:
                line_h.append(i)
                count = 0
                break
    #need to find a pair of y cordinates to calculate x cordinates for the 2 boxes
    #just making the line points worth one pixel
    count =0
    while count<len(line_h)-1:
        if line_h[count]+1 == line_h[count+1]:
            line_h.remove(line_h[count])
        else:
            count+=1
    first = line_h[0]
    second = line_h[1]
    line_v = []
    #finding the vertical line points
    for i in range(img.width):
        flag = True
        for j in range(first,second):
            if pixels[j][i] != 0:
                flag = False
                break
        if flag:
            line_v.append(i)

    count =0
    while count<len(line_v)-1:
        if line_v[count]+1 == line_v[count+1]:
            line_v.remove(line_v[count])
        else:
            count+=1

#getting the list of courses and their description using OCR
courses = []
for i in range(len(line_h)-1):
  courses.append(re.sub("\n"," ",pytesseract.image_to_string(pixels[line_h[i]:line_h[i+1], line_v[0]:line_v[1]],config='--psm 6')))
descriptions = []
for i in range(len(line_h)-1):
  descriptions.append(re.sub("\n"," ",pytesseract.image_to_string(pixels[line_h[i]:line_h[i+1], line_v[2]:line_v[3]],config='--psm 6')))

#Removing the course number and other gibresh from the course name
for i in range(len(courses)):
  course = courses[i]
  new = ''
  flag = False
  for j in [*course]:
    if flag:
      new += j
    if j == ")":
      flag = True
  courses[i] = new

print(courses)

pattern = re.compile(r'\b(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)\b')
date_P = r'\d{1,2}/\d{1,2}/\d{4}'
time_P = r'\b\d{1,2}:\d{2}(?:AM|PM)\b'
r_pattern = r'Room \b\d{3}\b'
del_list = []
days_mapping = {
    "Monday": MO,
    "Tuesday": TU,
    "Wednesday": WE,
    "Thursday": TH,
    "Friday": FR,
}
dates = []
rooms = []
times = []
days = []
# using pattern matching to get info from descriptions
for i in range(len(descriptions)):
  desc = descriptions[i]
  dates.append(re.findall(date_P, desc))
  rooms.append(re.findall(r_pattern, desc))
  times.append(re.findall(time_P, desc))
  index = 0
  n = []
  #This groups the days that appear next to each other together in a list. Like
  # Monday,Wednesday would be together.
  matches = pattern.finditer(desc)
  for j in matches:
    start_position = j.start()
    end_position = j.end()
    if index+15 < start_position:
      days.append(n)
      n = [j.group(0)]
    else:
      n.append(j.group(0))
    index = j.end()
  days.append(n)

#Extracting the buildings from the description by finding the occurences of the
#room nums and adding the comma seperated part of desc before it.
buildings = []
for i in range(len(descriptions)):
  n = []
  count = -1
  desc_list = descriptions[i].split(", ")
  for room in rooms[i]:
    for part in range(len(desc_list)):
      if len(desc_list[part]) >= len(room):
        if desc_list[part][0:len(room)] == room:
          if count >= 0:
            if desc_list[part-1] != n[count]:
              n.append(desc_list[part-1])
              count += 1
          else:
            n.append(desc_list[part-1])
            count += 1
  buildings.append(n)

#This removes the repitions in days
for i in range(1,len(days)):
  if (days[i] == days[i-1]):
    del_list.append(i)

neg = 0
for i in del_list:
  del days[i-neg]
  neg += 1
count = -1
ndays = []
print(days)
for i in range(len(days)):
  if days[i] == []:
    ndays.append([])
    count += 1
    continue
  for j in range(len(days[i])):
    days[i][j] = days_mapping[days[i][j]]
  ndays[count].append(tuple(days[i]))
print(ndays)

ntimes = []
for i in times:
  n = []
  count = 0
  for j in range(0, len(i), 2):
    if j+1<len(i):
      n.append((time_to_TDelta(i[j]),time_to_TDelta(i[j+1])))
  ntimes.append(n)
print(ntimes)

print(buildings)
print(rooms)
print(ndays[1][0][0])

cal = Calendar()
start_date = datetime(2023, 8, 21)
end_date = datetime(2023, 12, 15)
for i in range(len(ndays)):
  nevent = len(ndays[i])
  for j in range(nevent):
    rday = ndays[i][j]
    timeT = ntimes[i][j]
    time_diff = timedelta(hours=timeT[1].hour, minutes=timeT[1].minute) - timedelta(hours=timeT[0].hour, minutes=timeT[0].minute)
    rrule_params = {
    'freq': WEEKLY,
    'byweekday': rday,
    'dtstart': datetime.combine(start_date, timeT[0]),
    'until': datetime.combine(end_date, timeT[0]),
     }
    event_schedule = rrule(**rrule_params)
    for event_time in event_schedule:
      event_end = event_time + time_diff
      event = Event()
      event.add('summary', courses[i])
      event.add('dtstart', event_time)
      event.add('dtend', event_end)
      cal.add_component(event)

with open('recurring_event.ics', 'wb') as f:
    f.write(cal.to_ical())

print("iCalendar file 'recurring_event.ics' created.")


