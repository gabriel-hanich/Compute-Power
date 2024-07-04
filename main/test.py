

def calculateYVal(x):
    return x**2+1

def trapezoidalRule(x, y):
    area = 0

    for xIndex, xVal in enumerate(x):
        if xIndex != len(x) - 1:
            # 0.5 * h * (y1+y2)
            area += 0.5 * abs(xVal - x[xIndex+1]) * (y[xIndex] + y[xIndex+1])
        
    return area

x = []
y = []
for i in range(10):
    x.append(i)
    y.append(calculateYVal(i))

print(x)
print(y)


print(trapezoidalRule(x, y))