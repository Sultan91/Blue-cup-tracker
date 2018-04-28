import numpy as np
import cv2

def setup_ROI_for_tracking(roi) :
    hsv_roi =  cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_roi, np.array((0., 60.,32.)), np.array((180.,255.,255.)))
    roi_hist = cv2.calcHist([hsv_roi],[0],mask,[180],[0,180])
    cv2.normalize(roi_hist,roi_hist,0,255,cv2.NORM_MINMAX)
    return roi_hist

def draw_on_image(
    frame,
    track_window, 
    track_window2, 
    prob_count, 
    prob_count2, 
    previous_status, 
    i, 
    path_to_save,
    debug) :
    x,y,w,h = track_window
    x2,y2,w2,h2 = track_window2

    if prob_count>300:
        if(previous_status == 0):
            cv2.putText(frame,"Appeared", (200,60), cv2.FONT_HERSHEY_SIMPLEX, 3, (55,85,255),3)
            outfile =path_to_save+'pic%s.jpg' % (i)
            cv2.imwrite(outfile, frame)
            i+=1
		#frame = cv2.rectangle(frame, (x2,y2), (x2+w2,y2+h2), 255,2)
		#frame = cv2.rectangle(frame, (x,y), (x+w,y+h), 155,3)
        previous_status = 1;
    elif(prob_count<50):
        if(previous_status==1):
            outfile = path_to_save+'pic%s.jpg' % (i)
            cv2.putText(frame,"Dissapeared", (200,60), cv2.FONT_HERSHEY_SIMPLEX, 3, (255,25,255),3)
            cv2.imwrite(outfile, frame)
            i+=1
        previous_status = 0;

    return previous_status, frame, i


def do_detection(
    video_path='cup_detection/media/2018-02-2715_03_24.mp4',
    frame_path='cup_detection/static/images/frame.jpg',
    path_to_save_img='/cup_detection/static/images/pics/',
    path_to_save_video='/cup_detection/static/media/output.avi',
    debug=False) :

    import warnings
    import os

    warnings.filterwarnings("ignore")
    cap = cv2.VideoCapture(os.getcwd() + '/' + video_path)

    if not cap.isOpened():
        print('Video not available')
        exit(0)

    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))
    fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
    print(path_to_save_video)
    out = cv2.VideoWriter('cup_detection/media/output.avi', fourcc, 10.0, (frame_width,frame_height))

    if not out.isOpened():
        print('Video output not available')
        exit(0)

    frame = cv2.imread(frame_path)
    if frame is None:
        print("FRAME not available!")
        exit(0)

    # setup initial location of window cup
    r,w,c,h = 650,300,160,320  
    track_window = (r,c,w,h)
    roi_hist = setup_ROI_for_tracking(frame[c:c+h, r:r+w])

    r,w,c,h = 690,130,235,75  
    track_window2 = (r,c,w,h)
    roi_hist2 = setup_ROI_for_tracking(frame[c:c+h, r:r+w])

    # Setup the termination criteria, either 10 iteration or move by at least 1 pt
    term_crit = ( cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 1 )

    i=0
    previous_status = 2; # 0,1,2 - 1 preasent, 0 - absent previous status
    while(1):
        ret ,frame = cap.read()
        
        if ret == True:
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            dst = cv2.calcBackProject([hsv],[0],roi_hist,[0,180],1)

            # apply meanshift to get the new location
            ret, track_window = cv2.CamShift(dst, track_window, term_crit)
            
            dst2 = cv2.calcBackProject([hsv],[0],roi_hist2,[0,180],1)
            # apply meanshift to get the new location
            ret, track_window2 = cv2.CamShift(dst2, track_window2, term_crit)
            prob_count = np.count_nonzero(dst>250)
            prob_count2 = np.count_nonzero(dst2>250)

            previous_status, frame, i = draw_on_image(
                frame,
                track_window, 
                track_window2, 
                prob_count, 
                prob_count2, 
                previous_status, 
                i, 
                path_to_save_img,
                debug)

            out.write(frame)

            if debug:
                cv2.imshow('img2',frame)
                k = cv2.waitKey(60) & 0xff
                if k == 27:
                    break
        else:
            break
    if debug:
        cv2.destroyAllWindows()
    out.release()
    cap.release()
