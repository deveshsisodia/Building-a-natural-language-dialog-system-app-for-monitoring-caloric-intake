import csv


class CSVData:
    def __init__(self, abs_file_path):
        self.file_path = abs_file_path
        self.food_tokens = ''
        self.data_dict = dict()
        self._fill_data_members()

    def _fill_data_members(self):
        self.food_tokens = self.file_path.split('/')[-1].split('.')[0]
        with open(self.file_path, 'r', encoding='latin-1') as csv_file:
            reader = list(csv.reader(csv_file))
            for i in range(0, len(reader)):
                if len(reader[i]) > 0:
                    if reader[i][0] == 'Nutrient':
                        self.data_dict['Nutrient'] = list()
                        self.data_dict['Nutrient'].append(reader[i])
                    elif reader[i][0] == 'Proximates':
                        self.data_dict['Proximates'] = list()
                        i += 1
                        while reader[i][0] != 'Minerals':
                            if len(reader[i]) > 0:
                                self.data_dict['Proximates'].append(reader[i])
                            i += 1
                    elif reader[i][0] == 'Minerals':
                        self.data_dict['Minerals'] = list()
                        i += 1
                        while reader[i][0] != 'Vitamins':
                            if len(reader[i]) > 0:
                                self.data_dict['Minerals'].append(reader[i])
                                i += 1
                    elif reader[i][0] == 'Vitamins':
                        i += 1
                        self.data_dict['Vitamins'] = list()
                        while reader[i][0] != 'Lipids':
                            if len(reader[i]) > 0:
                                self.data_dict['Vitamins'].append(reader[i])
                                i += 1
                    elif reader[i][0] == 'Lipids':
                        self.data_dict['Lipids'] = list()
                        i += 1
                        while reader[i][0] != 'Amino Acids':
                            if len(reader[i]) > 0:
                                self.data_dict['Lipids'].append(reader[i])
                                i += 1
                    elif reader[i][0] == 'Amino Acids':
                        self.data_dict['Amino Acids'] = list()
                        i += 1
                        while reader[i][0] != 'Other':
                            if len(reader[i]) > 0:
                                self.data_dict['Amino Acids'].append(reader[i])
                                i += 1
                    elif reader[i][0] == 'Other':
                        self.data_dict['Other'] = list()
                        i += 1
                        while i < len(reader):
                            if len(reader[i]) > 0:
                                self.data_dict['Other'].append(reader[i])
                                i += 1
                    else:
                        pass