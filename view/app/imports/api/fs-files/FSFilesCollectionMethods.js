import { ValidatedMethod } from 'meteor/mdg:validated-method';
import { SimpleSchema } from 'meteor/aldeed:simple-schema';
import { FSFiles } from './FSFilesCollection';
import { FSChunks } from '../fs-chunks/FSChunksCollection';

export const getEventData = new ValidatedMethod({
  name: 'FSFiles.getEventData',
  validate: new SimpleSchema({
    filename: { type: String },
  }).validator({ clean: true }),
  run({ filename }) {
    if (!this.isSimulation) {
      // Get file and chunks
      const file = FSFiles.findOne({ filename });
      const chunks = FSChunks.find({ files_id: file._id }, { sort: { n: 1 } }).fetch();

      // Gridfs seems to store chunks as
      // Need to parse binary data chunks as 16-bit signed int.
      const int16Chunks = []; // Array of chunks.
      let totalSize = 0;
      chunks.forEach(chunk => {
        const u8 = new Uint8Array(chunk.data);
        const s16 = new Int16Array(u8.buffer);
        int16Chunks.push(s16);
        totalSize += s16.length;
      });

      // Flatten/combine all chunks to a single array.
      const combinedInt16Chunks = new Int16Array(totalSize);
      let offset = 0;
      int16Chunks.forEach((chunk) => {
        combinedInt16Chunks.set(chunk, offset);
        offset += chunk.length;
      });

      return Array.from(combinedInt16Chunks); // Return data as regular array.
    }
    return null;
  },
});
