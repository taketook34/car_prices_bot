import json
import pandas
from sklearn.linear_model import LinearRegression



class NotExistCarsError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class ElectroCarError(Exception):
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class PriceAnalyzer:
    def __init__(self, mark, model, fueltype, folder_dir='parser'):
        self.fueltype = fueltype

        with open(f'{folder_dir}/{mark}_{model}.json', 'r') as file:
            data = json.load(file)
            main_df = pandas.DataFrame(data)
            file.close()
        
        if main_df.empty:
            raise ElectroCarError('Введен електрокар')
        
        if self.fueltype not in main_df['fueltype'].unique():
            raise NotExistCarsError('Нету даной модели с заданым типом топлива')
        
        train_x = main_df[main_df['fueltype'] == self.fueltype][[ 'oddmeter', 'engine_V', 'transmission', 'year']].values
        train_y = main_df[main_df['fueltype'] == self.fueltype]['price'].values

        self.ln_model = LinearRegression()
        self.ln_model.fit(train_x, train_y)

    def get_predict(self, input_data: list):
        return self.ln_model.predict([input_data])
        
# car = PriceAnalyzer('mazda', 'cx-3', 'Дизель')
# print(car.get_predict([1000, 3, 4, 3]))