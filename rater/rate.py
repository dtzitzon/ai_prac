import json

def main():

    data = None
    with open("Brown_University.json", 'r') as jsonFile:
        data = json.load(jsonFile)
        print(jsonFile)

    yaks = data["yacks"]

    numyaks = 0
    ratedYaks = []
    print("[p] for positive; [o] for neutral; [n] for negative; [s] to save")
    for yak in yaks:
        print("Message "+str(numyaks)+": " + yak["message"])
        while True:
            commandline = input("Rate: ")
            commandline = commandline.strip()
            pieces = commandline.split(" ")

            if pieces[0] == "p":
                yak["sentiment"] = "positive"
                ratedYaks.append(yak)
                numyaks +=1
                break
            elif pieces[0] == "o":
                yak["sentiment"] = "neutral"
                ratedYaks.append(yak)
                numyaks +=1
                break
            elif pieces[0] == "n":
                yak["sentiment"] = "negative"
                ratedYaks.append(yak)
                numyaks +=1
                break
            elif pieces[0] == "s":
                print("saved")
                with open('brownrated.json', 'w') as outfile:
                    outfile.write(str(json.dumps(ratedYaks, ensure_ascii=False)))
            else:
                print("input '" + pieces[0] + "' not recognized")


    with open('brownrated.json', 'w') as outfile:
        outfile.write(str(json.dumps(ratedYaks, ensure_ascii=False)))

main()
