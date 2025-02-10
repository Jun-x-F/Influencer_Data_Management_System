import elTableInfiniteScroll from 'el-table-infinite-scroll';
import type {ObjectDirective, Plugin} from 'vue';

export default function directive(app: { directive: (arg0: string, arg1: ObjectDirective<any, any, string, string> & Plugin) => void; }) {
    app.directive('elTableInfiniteScroll', elTableInfiniteScroll);
}