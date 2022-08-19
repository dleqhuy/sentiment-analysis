from keras.preprocessing.sequence import pad_sequences
from keras.layers import Dense, Embedding, LSTM, Input, Conv1D, MaxPooling1D, GlobalMaxPooling1D
from keras.models import Model, Sequential, load_model
from tensorflow.keras.utils import to_categorical
from keras.callbacks import TensorBoard, ModelCheckpoint
from keras.preprocessing.text import Tokenizer
import unicodedata
import pandas as pd
import os
import numpy as np
import pickle
import numpy as np


def saveByPickle(object, path):
    pickle.dump(object, open(path, "wb"))
    print(f"{object} has been saved at {path}.")

def convertToNFX(series, type: str):
    return series.apply(lambda x: unicodedata.normalize(type, x))

def loadByPickle(path):
    with open(path, 'rb') as f:
        return pickle.load(f)

class SentimentLSTM:
    def __init__(self, pmodel_path:str=None, ptokenizer_path:str=None) -> (None):
        if pmodel_path and ptokenizer_path:
            self.model = load_model(pmodel_path)
            (self.tokenizer, self.embedding_dim) = loadByPickle(ptokenizer_path)
    
    def _initTokenizer(self, pdata: pd.Series, pnum_words:int=None):
        self.tokenizer = Tokenizer(num_words=pnum_words)
        self.tokenizer.fit_on_texts(pdata)
        
    def _callback(self, pname):
        tensorboard_callback = TensorBoard(log_dir=os.path.join(os.getcwd(), "tb_log_sentiment", pname), write_graph=True,
                                       write_grads=False)
        checkpoint_callback = ModelCheckpoint(filepath=pname + "/weights/" + "{epoch:02d}-{val_loss:.6f}.h5",
                                          monitor='val_loss', verbose=0, save_best_only=True)
        return [tensorboard_callback, checkpoint_callback]
        
    def _defineModel(self, pno_units:int=10, pdropout:float=0.2, poptimizer:str='adam'):
        vocab_size = len(self.tokenizer.word_index) + 1
        self.embedding_dim = self.X.shape[1]
        self.model = Sequential()
        self.model.add(Input(shape=(self.embedding_dim,), name='input'))
        self.model.add(Embedding(vocab_size, self.embedding_dim, input_length=100, name='embedding'))
        self.model.add(LSTM(units=pno_units, dropout=pdropout, recurrent_dropout=pdropout, name='lstm'))
        self.model.add(Dense(2, activation='softmax', name='output'))
        self.model.compile(loss='binary_crossentropy', optimizer=poptimizer, metrics=['accuracy'])
        
            
    def define(self, pX, py, pnum_words:int=None, pseq_length:int=None, poptimizer:str='adam', pno_units:int=10, pdropout:float=0.2, **kwargs):
        pX = convertToNFX(pX, 'NFC')
        self._initTokenizer(pdata=pX, pnum_words=pnum_words)  
        self.X = pad_sequences(self.tokenizer.texts_to_sequences(pX), maxlen=pseq_length)
        self.y = to_categorical(py)        
        self._defineModel(pno_units, pdropout, poptimizer)
        
    def fit(self, pbatch_size:int=32, pepochs:int=10, psave_weights:str=None, **kwargs):
        self.model.fit(self.X, self.y, batch_size=pbatch_size, epochs=pepochs,
                       validation_split=0.1, callbacks=self._callback(psave_weights[:-3]))
              
    def predict(self, pnew_data):
        new_data = self.tokenizer.texts_to_sequences(convertToNFX(pnew_data, 'NFC'))
        new_data = pad_sequences(new_data, maxlen=self.embedding_dim)
        yhat_proba = self.model.predict(new_data)

        return pd.DataFrame({
            'input': pnew_data,
            'output_proba': [tuple(x) for x in yhat_proba],
            'output_class': np.argmax(yhat_proba, axis=1)
        })
        
    def evaluation(self):
        ixs = np.random.choice(self.X.shape[0], int(self.X.shape[0]*0.1), replace=False)
        loss = self.model.evaluate(self.X[ixs], self.y[ixs])
        
        return loss[0]
        
    def getTokenizerWordIndex(self):
        return self.tokenizer.word_index
    
    def save(self, pmodel_path:str, ptoken_path:str):
        self.model.save(pmodel_path)
        saveByPickle((self.tokenizer, self.X.shape[1]), ptoken_path)
        print(f"📢 Model has been saved at {pmodel_path} - Tokenizer has been saved at {ptoken_path}.") 
        