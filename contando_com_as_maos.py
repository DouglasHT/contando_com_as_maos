#importacoes
import cv2
import numpy as np
import math

#captura de video
cap = cv2.VideoCapture(0)
#contador de tempo
timer = 0
#contador de "joia"
y = 0
#carregando
dot = 0

#Inicio do loop para a captura dos frames
while(1):


    # Trata o erro de não ter nenhum contorno dentro do retangulo
    try:

        # 1.Captura quadro a quadro
        ret,frame = cap.read()
        # 2.Inverte a imagem horizontalmente
        frame = cv2.flip(frame,1)
        # 3.Devolve uma nova matriz de forma e tipo dados, preenchidos com uns.
        # np.one(tamanho da matriz,tipo de dados) o np.uint8 e padrao
        kernel = np.ones((3,3),np.uint8)

        # 4.Define a regiao de interesse
        roi = frame[100:300, 100:300]

        # 5.Desenha um retângulo do tamanho do frame capturado
        cv2.rectangle(frame, (100,100), (300,300), (0,255,0), 0)
        # 6.Pega a imagem em BGR e converte para cinza em HSV
        hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

        # 7.Define o intervalo da cor da pele no HSV
        lower_skin = np.array([0,20,70], dtype=np.uint8)
        upper_skin = np.array([20,255,255], dtype=np.uint8)

        # 8.Limita a imagem do HSV para obter apenas as cores da pele
        mask = cv2.inRange(hsv, lower_skin, upper_skin)

        # 9.Aumenta a parte branca considera todos os pixels mesmo que nao forem
        # totalmente 1
        mask = cv2.dilate(mask, kernel, iterations=4)

        # 10.Remove conteúdo de alta frequência
        #(por exemplo, ruído, bordas) da imagem
        mask = cv2.GaussianBlur(mask,(5,5),100)

        # 11.Encontrando contornos
        _,contours,hierarchy= cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)

        # 12.Encontrando contorno da area maxima(mao),acompanha o tamanho da mao
        cnt = max(contours, key = lambda x: cv2.contourArea(x))

        # 13.Aproxima o contorno um pouco
        epsilon = 0.0005*cv2.arcLength(cnt,True)
        approx= cv2.approxPolyDP(cnt,epsilon,True)

        # 14.Faz meio que um casco convexo em volta do tamanho
        hull = cv2.convexHull(cnt)

        # 15.Define a area do casco e a area da mao
        areahull = cv2.contourArea(hull)
        areacnt = cv2.contourArea(cnt)

        # 16.Encontra a porcentagem da area nao convertida do tamanho
        # em um casco convexo
        arearatio=((areahull-areacnt)/areacnt)*100

        # 17.Encontrar os desvios no casco convexo em relacao a mao
        hull = cv2.convexHull(approx, returnPoints=False)
        defects = cv2.convexityDefects(approx, hull)

        # 18.l = no(false). contador de desvios
        l=0

        # 19.Codigo para encontrar os espacos nos desvios dos dedos
        for i in range(defects.shape[0]):
            s,e,f,d = defects[i,0]
            start = tuple(approx[s][0])
            end = tuple(approx[e][0])
            far = tuple(approx[f][0])
            pt= (100,180)

            # 20. Encontra o comprimento de todos os lados do triangulo
            a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
            b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
            c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)
            s = (a+b+c)/2
            ar = math.sqrt(s*(s-a)*(s-b)*(s-c))

            # 21.Distancia entre ponto e cascos convexos
            angle = math.acos((b**2 + c**2 - a**2)/(2*b*c)) * 57

            # 22. Ignora angulos > 90 e ignora pontos muito perto do casco convexos
            #geralmente sao resultantes de ruidos
            if angle <= 90 and d>30:
                l += 1
                cv2.circle(roi, far, 3, [255,0,0], -1)

            # Desenha linhas em volta da mao
            cv2.line(roi,start, end, [0,255,0], 2)


        l+=1



        # 23.Imprime um texto no caso numero correspondente ao gesto feito
        if timer%30==0:
            font = cv2.FONT_HERSHEY_SIMPLEX
            if l==1:
                if arearatio<12:
                    x = 0
                elif arearatio<17.5:
                    if y>0:
                        y=0
                    else:
                        cv2.putText(frame,"salvando...",(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
                        y+=1
                else:
                    x = 1

            elif l==2:
                x = 2

            elif l==3:
                if arearatio<27:
                    x = 3

            elif l==4:
                x = 4

            elif l==5:
                x = 5




        # Calculo
        if y==0:
            x1 = x
            conta = x1
            strconta = (str(x1))

        elif y>0:
            x2 = x
            #se quiser alterar a operacao eh so mudar esse linha
            conta = x1 + x2 #se quiser alterar a operacao eh so mudar esse linha
            strconta = (str(x1) + "+" + str(x2) + "=" + str(conta))#Passando a conta para string

        #Mostra o texto na imagem
        #cv2.putText(frame,"                "+str(y),(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)
        cv2.putText(frame,str(strconta),(0,50), font, 2, (0,0,255), 3, cv2.LINE_AA)

        cv2.imshow('mask',mask)
        cv2.imshow('frame',frame)


        #print(timer)
        timer += 1
    except:
        dot+=1
        cv2.putText(frame,"Aguardando",(0,50), font, 1, (0,0,255), 3, cv2.LINE_AA)
        #Se tirar essa linha,o programa para de rodar se nao houver nada dentro
        #do retangulo e so volta quando houver
        if dot>7 and dot<15:
            cv2.putText(frame,"            "+".",(0,50), font, 1, (0,0,255), 3, cv2.LINE_AA)
        elif dot>17 and dot<25:
            cv2.putText(frame,"            "+"..",(0,50), font, 1, (0,0,255), 3, cv2.LINE_AA)
        elif dot>27 and dot<35:
            cv2.putText(frame,"            "+"...",(0,50), font, 1, (0,0,255), 3, cv2.LINE_AA)
        elif dot==35:
            dot = 0

        cv2.imshow('frame',frame)
        pass


    k = cv2.waitKey(10)
    if k == 27:
        break
