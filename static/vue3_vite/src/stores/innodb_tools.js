/**
 * IndexedDB Helper Class
 * 封装了常用的 IndexedDB 操作，使用 Promises 和 async/await 语法
 */
export default class IndexedDBHelper {
    /**
     * 构造函数
     * @param {string} dbName - 数据库名称
     * @param {number} dbVersion - 数据库版本
     * @param {Object} storeSchemas - 对象存储的模式定义
     *        格式：
     *        {
     *            storeName1: { keyPath: 'id', autoIncrement: true, indexes: ['field1', 'field2'] },
     *            storeName2: { keyPath: 'uniqueId', autoIncrement: false, indexes: ['fieldA', 'fieldB'] },
     *            ...
     *        }
     */
    constructor(dbName, dbVersion, storeSchemas) {
        this.dbName = dbName;
        this.dbVersion = dbVersion;
        this.storeSchemas = storeSchemas;
        this.db = null;
    }

    /**
     * 打开数据库，若不存在则创建
     * @returns {Promise<IDBDatabase>}
     */
    openDatabase() {
        return new Promise((resolve, reject) => {
            const request = indexedDB.open(this.dbName, this.dbVersion);

            request.onupgradeneeded = (event) => {
                const db = event.target.result;
                const oldVersion = event.oldVersion;
                const newVersion = event.newVersion || db.version;

                // 创建或更新对象存储
                for (const [storeName, schema] of Object.entries(this.storeSchemas)) {
                    if (!db.objectStoreNames.contains(storeName)) {
                        const objectStore = db.createObjectStore(storeName, {
                            keyPath: schema.keyPath,
                            autoIncrement: schema.autoIncrement || false
                        });
                        // 创建索引
                        if (schema.indexes && Array.isArray(schema.indexes)) {
                            schema.indexes.forEach(index => {
                                objectStore.createIndex(index, index, { unique: false });
                            });
                        }
                    } else {
                        // 如果需要更新索引，可以在这里处理
                        const objectStore = request.transaction.objectStore(storeName);
                        if (schema.indexes && Array.isArray(schema.indexes)) {
                            schema.indexes.forEach(index => {
                                if (!objectStore.indexNames.contains(index)) {
                                    objectStore.createIndex(index, index, { unique: false });
                                }
                            });
                        }
                    }
                }
            };

            request.onsuccess = (event) => {
                this.db = event.target.result;
                // Handle database close event
                this.db.onclose = () => {
                    console.warn(`数据库 "${this.dbName}" 已关闭`);
                };
                resolve(this.db);
            };

            request.onerror = (event) => {
                console.error(`打开数据库 "${this.dbName}" 失败:`, event.target.error);
                reject(event.target.error);
            };

            request.onblocked = () => {
                console.warn(`打开数据库 "${this.dbName}" 被阻塞`);
            };
        });
    }

    /**
     * 验证数据对象是否包含必要的 keyPath
     * @param {string} storeName - 对象存储名称
     * @param {Object} data - 数据对象
     * @throws {Error} 如果验证失败
     */
    validateData(storeName, data) {
        const schema = this.storeSchemas[storeName];
        if (!schema) {
            throw new Error(`对象存储 "${storeName}" 的模式未定义`);
        }

        const keyPath = schema.keyPath;
        const hasKey = keyPath in data;

        if (!schema.autoIncrement && !hasKey) {
            throw new Error(`数据对象缺少 keyPath "${keyPath}"，无法在对象存储 "${storeName}" 中添加/更新`);
        }
    }

    /**
     * 添加或更新数据
     * @param {string} storeName - 对象存储名称
     * @param {Object} data - 要添加或更新的数据
     * @returns {Promise<void>}
     */
    addOrUpdateData(storeName, data) {
        return new Promise((resolve, reject) => {
            try {
                this.validateData(storeName, data);
            } catch (validationError) {
                console.error(validationError.message);
                reject(validationError);
                return;
            }

            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const request = store.put(data);

            request.onsuccess = () => {
                resolve();
            };

            request.onerror = (event) => {
                console.error(`添加/更新数据失败在对象存储: ${storeName}`, event.target.error);
                reject(event.target.error);
            };
        });
    }

    /**
     * 获取单条数据
     * @param {string} storeName - 对象存储名称
     * @param {IDBValidKey} key - 主键值
     * @returns {Promise<Object|null>}
     */
    getData(storeName, key) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const request = store.get(key);

            request.onsuccess = (event) => {
                const result = event.target.result;
                resolve(result || null);
            };

            request.onerror = (event) => {
                console.error(`获取数据失败在对象存储: ${storeName}`, event.target.error);
                reject(event.target.error);
            };
        });
    }

    /**
     * 获取所有数据
     * @param {string} storeName - 对象存储名称
     * @returns {Promise<Array>}
     */
    getAllData(storeName) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const request = store.getAll();

            request.onsuccess = (event) => {
                const result = event.target.result;
                resolve(result);
            };

            request.onerror = (event) => {
                console.error(`获取所有数据失败在对象存储: ${storeName}`, event.target.error);
                reject(event.target.error);
            };
        });
    }

    /**
     * 根据索引获取数据
     * @param {string} storeName - 对象存储名称
     * @param {string} indexName - 索引名称
     * @param {any} query - 查询条件
     * @returns {Promise<Array>}
     */
    getDataByIndex(storeName, indexName, query) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readonly');
            const store = transaction.objectStore(storeName);
            const index = store.index(indexName);
            const request = index.getAll(query);

            request.onsuccess = (event) => {
                const result = event.target.result;
                resolve(result);
            };

            request.onerror = (event) => {
                console.error(`通过索引 "${indexName}" 获取数据失败在对象存储: ${storeName}`, event.target.error);
                reject(event.target.error);
            };
        });
    }

    /**
     * 删除单条数据
     * @param {string} storeName - 对象存储名称
     * @param {IDBValidKey} key - 主键值
     * @returns {Promise<void>}
     */
    deleteData(storeName, key) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const request = store.delete(key);

            request.onsuccess = () => {
                resolve();
            };

            request.onerror = (event) => {
                console.error(`删除数据失败在对象存储: ${storeName}`, event.target.error);
                reject(event.target.error);
            };
        });
    }

    /**
     * 清空对象存储中的所有数据
     * @param {string} storeName - 对象存储名称
     * @returns {Promise<void>}
     */
    clearStore(storeName) {
        return new Promise((resolve, reject) => {
            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);
            const request = store.clear();

            request.onsuccess = () => {
                resolve();
            };

            request.onerror = (event) => {
                console.error(`清空对象存储失败在对象存储: ${storeName}`, event.target.error);
                reject(event.target.error);
            };
        });
    }

    /**
     * 批量添加或更新数据
     * @param {string} storeName - 对象存储名称
     * @param {Array<Object>} dataArray - 要添加或更新的数据数组
     * @returns {Promise<void>}
     */
    addOrUpdateDataBatch(storeName, dataArray) {
        return new Promise((resolve, reject) => {
            if (!Array.isArray(dataArray)) {
                reject(new Error(`数据数组必须为数组类型`));
                return;
            }

            // Validate all data objects before proceeding
            try {
                dataArray.forEach(data => this.validateData(storeName, data));
            } catch (validationError) {
                console.error(validationError.message);
                reject(validationError);
                return;
            }

            const transaction = this.db.transaction([storeName], 'readwrite');
            const store = transaction.objectStore(storeName);

            transaction.oncomplete = () => {
                resolve();
            };

            transaction.onerror = (event) => {
                console.error(`批量添加/更新数据失败在对象存储: ${storeName}`, event.target.error);
                reject(event.target.error);
            };

            transaction.onabort = (event) => {
                console.error(`事务中止: 批量添加/更新数据失败在对象存储: ${storeName}`, event.target.error);
                reject(event.target.error);
            };

            dataArray.forEach(data => {
                store.put(data);
            });
        });
    }

    /**
     * 关闭数据库连接
     */
    closeDatabase() {
        if (this.db) {
            this.db.close();
            console.log(`已关闭数据库 "${this.dbName}" 连接`);
            this.db = null;
        }
    }
}
