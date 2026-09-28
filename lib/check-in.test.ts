import { describe, expect, it } from 'vitest';
import { decideCheckIn, type CheckInCandidate } from './check-in';

const valid: CheckInCandidate = { memberActive:true, subscriptionActive:true, startDate:'2026-01-01', endDate:'2026-12-31', remainingVisits:5, lastCheckInAt:null };
const now = new Date('2026-06-10T10:00:00.000Z');
describe('decideCheckIn',()=>{
  it('cho phép và trừ lượt với gói theo lượt',()=>expect(decideCheckIn(valid,now)).toEqual({ok:true,decrementVisit:true}));
  it('không trừ lượt với gói không giới hạn',()=>expect(decideCheckIn({...valid,remainingVisits:null},now)).toEqual({ok:true,decrementVisit:false}));
  it.each([
    [{...valid,memberActive:false},'MEMBER_INACTIVE'],
    [{...valid,subscriptionActive:false},'NO_ACTIVE_SUBSCRIPTION'],
    [{...valid,startDate:'2026-07-01'},'NOT_STARTED'],
    [{...valid,subscriptionFrozen:true},'FROZEN'],
    [{...valid,endDate:'2026-06-09'},'EXPIRED'],
    [{...valid,remainingVisits:0},'NO_VISITS_LEFT'],
    [{...valid,lastCheckInAt:new Date('2026-06-10T09:55:00.000Z')},'DUPLICATE'],
  ] as const)('từ chối đúng quy tắc %#',(candidate,reason)=>expect(decideCheckIn(candidate,now)).toEqual({ok:false,reason}));
});
