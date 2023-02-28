# ErythrocytesIDB2

The images consist of peripheral blood smears samples of patients with sickle cell anaemia classified by a specialist from *Dr. Juan Bruno Zayas* Hospital General in Santiago de Cuba, Cuba. The specialist's criteria is used as an expert approach to validate the results of the classification methods used in this work.

The dataset consists of 50 different samples of patients with sickle cell anaemia. The file structure is a folder for each sample. Each folder follows the next structure:



```
​```
├── source.jpg			<- Sample of patients with sickle cell anaemia
├── labeled.jpg			<- Image classified by the specialist
├── mask.jpg          	<- Binary mask with all the cells (without any distintion by type)
├── mask-circular.jpg	<- Binary mask with all circular cells.
├── mask-elongated.jpg	<- Binary mask with all elongated cells.
├── mask-other.jpg		<- Binary mask with all other cells
└── ground.csv			<- Files containing a contour for each cell
​```
```



The different mask files can contain overlapped objects. To handle this situation on the overlapped zone a value of 0.5 is used. 

The `ground.csv`contains the information of each cell. Each row is cell, the first column indicate the class {0=> circular, 1 => elongated and 2 => other} while the rest shows all the points that defines the contour. 