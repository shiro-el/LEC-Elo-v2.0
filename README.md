pip install pandas

pip install dataframe_image

# fetch.py, parse.py

lolesports api로부터 경기 정보를 불러와 match.csv에 저장해주는 코드입니다. 사용하지 말아주세요.

# analyze.py

match.csv와 initElo.csv로부터 정보를 불러와 예상값들을 연산해주고, lec.csv 파일에 저장해줍니다.

상세한 사용 방법은 후술되어있습니다.

# plot.py

lec.csv 파일에서 정보를 불러와 표로 만들어줍니다.

자유롭게 수정하셔도 됩니다.





# match.csv 경기정보 입력 양식

FNC,GX,1,1 (FNC 2:0 GX)

TH,RGE,0,1,0 (TH 1:2 RGE)

# analyze.py 경기 정보 입력 양식

G2,KC,3/FNC,MKOI,5

(G2 vs KC의 BO3, FNC vs MKOI BO5의 예상 결과를 알고 싶을 때)

필요한거 없으면 비워놓으셔도 됩니다.
