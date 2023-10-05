# Made by: Miguel Velasco Espinosa, Thompson Nguyen, and Fabiola Felipe
import sys
import wave
import math
from multiprocessing import Pool
import time
def main():
    #Gets raw data, samples per second, and total samples from wav file
    data, rate, totalframes = read_wav("sample.wav")
    f = data
    sectioned_f = []
    
    #Calculates total time of file
    seconds = int(totalframes/rate)

    #Splits sample into sub samples according to how many seconds the file lasts
    for i in range(seconds):
        sectioned_f.append(f[(i*rate):((i+1)*rate)])
        
    #Pool initialization for multithreading
    pool = Pool(6)
    #Pool function that calls fft function on each element in sectioned_f
    #and appends it to sectioned_PSD in the correct order
    sectioned_FFT = pool.map(fft, sectioned_f)

    #Threshold value for cutoff
    threshold = 6*10**9
    #Iterates through each element of sectioned_FFT and filters and thresholds values into a binary number
    #and appends it to eight_bit_list
    eight_bit_list = []
    for c in sectioned_FFT:
        fhat = c
        #Filter: checks index at each frequency and sets to 0 if it is not a wanted frequency
        for i in  range(len(fhat)):
            if(i%100==0):
                fhat[i] = fhat[i]
            else:
                fhat[i] = 0
        new_f = fhat[0:900]
        #Empty 8 bit list
        new_8_bit = []
        #Iterates through each frequency and checks if the peak is higher than a specific threshold
        for i in range(len(new_f)):
            if(i == 100 and (new_f[i].real > threshold)):
                #Appends 1 to a binary list if higher
                new_8_bit.append(1)
            elif(i == 100 and (new_f[i].real< threshold)):
                #Appends 0 to a binary list if lower
                new_8_bit.append(0)
            elif ((new_f[i].real > threshold) and ((i % 100 ==0)and (i>100))):
                #Appends 1 to a binary list if higher
                new_8_bit.append(1)
            elif((new_f[i].real < threshold) and ((i % 100 ==0)and (i>100))):
                #Appends 0 to a binary list if lower
                new_8_bit.append(0)
        eight_bit_list.append(new_8_bit)
    binary = []
    #Iterates through eight_bit _list and appends to a full list of binary codes
    for i in range(len(eight_bit_list)):
        t_binary = []   
        for j in eight_bit_list[i]:
            if j == 0:
                t_binary.append(0)
            else:
                t_binary.append(1)
        for k in range(1,8,1):
            binary.append(t_binary[k])
    #Converts to string
    string_decode = ''.join(str(x) for x in binary)
    text = "".join([chr(int(string_decode[i:i+7],2)) for i in range(0,len(string_decode),7)])
    print(text)
    with open("cap.txt", "w") as f:
        f.writelines(text)

#Opens wav file to read and extract data
def read_wav(path):
    #Opens path was a read only wav file
    with wave.open(path, "rb") as wav:
        #Finds nchannels, sampwidth, framerate, and nframes 
        nchannels, sampwidth, framerate, nframes, _, _ = wav.getparams()
        #Sets signed as values above 1 sampwidth
        signed = sampwidth > 1  
        byteorder = sys.byteorder  
        #Iterates through raw data and converts to integer amplitude values
        values = []  
        for _ in range(nframes):
            frame = wav.readframes(1)  
            #To bytes
            as_bytes = frame[0: sampwidth]
            #To int
            as_int = int.from_bytes(as_bytes, byteorder, signed=signed)
            values.append(as_int)
    return values, framerate , nframes      
def fft(D):
    Xk = []
    N =  len(D) #Gets the length of signal
    #This function runs after the if(N > 1) 
    def fun1():
        X = [] #Initializes values and lists needed
        pi = 180 #Pi in degrees
        b = 0
        while(b < m):
            X.append([]) #Creates a matrix for x
            k1 = 0
            while(k1 < N1):
                X[b].append(k1) #Appends k1 for the matrix
                X[b][k1] = 0 
                DFT = 0
                for n in range(0,(N1-1)+1): #The loop runs for how big N1 is
                    sr = math.cos(math.radians(2*pi*n*m*k1/N)) #Gets the real number and makes it a cosien
                    si = math.sin(math.radians((-1)*2*pi*n*m*k1/N))*(1j) #Gets the imaginary number and sets it as a sin
                    w = sr + si #Omega will be in the form cos() + jsin()
                    DFT = DFT + (D[(m*n) + b])*w #Sums up parts. Think of it this is inside a summation
                X[b][k1] = DFT #Adds the DFT to the X matrix
                k1 = k1+1
            b = b+1
        k = 0
        c = 0
        while(k < N):
            FFT = 0
            if(c == N1):
                c = 0
            for b in range(0,m): #repeats the same process as previous for loop
                sr = math.cos(math.radians(2*pi*b*k/N))
                si = math.sin(math.radians((-1)*2*pi*b*k/N))*(1j)
                w = sr + si
                FFT = FFT + (X[b][c])*w #This is all the summations summed up
            Xk.insert(k,FFT) #Inserts the FFT to respective index from 0 to 900
            c = c+1
            k = k +1 
    x = []
    for i in range (1,int(N/2)+1):
        if((N%i)==0): #Checks to see if N is divisible by half the length of the signal length e.g N = 1000 -> [1000 % 2 = 0 => True] -> [1000 % 3 = 1 => False]
            x.append(i) #append the number 
        else:
            x = x
    y = len(x)
    a = int(y/2)
    if((y%2)==0): #Checks to see if it is divisible by 2
        N1 = m = x[a] #Equals N1 and m to the number at the half of the array. This is because the length of x is divisible by two so N1 and m will be the same
        fun1() #Calls the function above
        return Xk #Returns the FT

if __name__ == '__main__':
    st = time.time()
    main()
    end = time.time()
    print("Time: ", (end - st), "Seconds")
