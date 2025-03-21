 请设计一套算法，实现下面场景的连线问题：
在现实环境中，一个小区有很多幢楼，而楼与楼之间存在很多管道需要连接，现在将该情况理想化成一个二维平面（xy平面），平面上有很多单元格，按行行列排列（N行M列），单元格中间有间隔空隙（比如30像素），管道连接就抽象成不同颜色的连线，这些连线从起始单元格，到达终点单元格，连线只允许在单元格的间隔空隙中绘制，连线必须是横平竖直，允许连线之间存在十字交叉，但不允许在连接有重叠。
已知有一组单元格连接请求序列,[row1,row2,...]，每行的信息为[cell1,cell2,...],平面中每个单元格宽高为50x50像素，单元格与单元格间隙为30像素。
每个单元格的rectangle信息，可以通过(row,col)获取到，返回不含间隙的单元格rectangle信息{top,left,right,bottom}。
每次连线的请求会提供起始和终点cell的坐标{start:[row1,col1],end:[row2,col2]}，要求计算出连线的结果，结果为折线,用2或3个点坐标(x,y)表示；
连线走向要求：
1. 起始单元格到终点单元格，连线要求：
1.1 如果在同一行，只允许一条水平线段连接，连线结果用[(x1,y),(x2,y)]表示，其中x1和x2是起始和终点单元格的中心点x坐标，y为取值根据起始cell和终点cell的相对位置进行选择：
1.1.1 如果start.col<end.col，为了避免重叠，则y的取值为单元格下方的空隙位置(bottom,bottom+30)；
1.1.2 如果start.col>end.col，为了避免重叠，则y的取值为单元格下方的空隙位置(top-30,top)；
1.2 如果是同一列，只允许一条垂直线段连接，连线结果用[(x,y1),(x,y2)]表示，其中y1和y2是起始和终点单元格的中心点y坐标，x为取值根据起始cell和终点cell的相对位置进行选择：
1.2.1 如果start.row<end.row，为了避免重叠，则x的取值为单元格右方的空隙位置(right,right+30)；
1.2.2 如果start.row>end.row，为了避免重叠，则x的取值为单元格左方的空隙位置(left-30,left)；

1.3 其它情况允许一条水平线段+一条垂直线段，连线结果用[(x1,y1),(x2,y1),(x2,y2)]表示，其中x1,y1,x2,y2的取值要求根据起始cell和终点cell的相对位置进行选择：



2. 根据终点单元格相对起始单元格的位置，设定不同的连线起始点坐标：
2.1 如果终点单元格在起点单元格的上方，即to.row<from.row，那么连线起始点就起始单元格的上边缘中点位置(x坐标为单元格的中心点x坐标），为了避免单元格上方有其它线段经过，允许线段起点的y值为单元格的上方间隙中取值(cell.top-30,cell.top)；
2.2 如果终点单元格在起点单元格的下方，即to.row>from.row，那么连线起始点就起始单元格的下边缘中点位置(x坐标为单元格的中心点x坐标），为了避免单元格下方有其它线段经过，允许线段起点的y值为单元格的下方间隙中取值(cell.top,cell.top+30)；
3. 根据终点单元格相对起始单元格的位置，设定不同的连线结束点坐标：
3.1 如果终点单元格在起点单元格的左侧，即to.col<from.col，那么连线终点在终点单元格的右侧，y坐标为单元格中心点的y值，而x坐标为了避免与其它垂直经过右侧的线段出现重叠，允许取值为(cell.right,cell.right+30)；
3.2 如果终点单元格在起点单元格的右侧，即to.col>from.col，那么连线终点在终点单元格的左侧，y坐标为单元格中心点的y值，而x坐标为了避免与其它垂直经过左侧的线段出现重叠，允许取值为(cell.right-30,cell.right)；

现在需要给出各组连线的具体连线坐标位置结果